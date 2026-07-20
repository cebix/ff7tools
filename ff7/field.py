#
# ff7.field - Final Fantasy VII field map and script handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct

from . import lzss
from . import ff7text


def _enum(**enums):
    return type('Enum', (), enums)


# Field map file sections
Section = _enum(EVENT = 0, WALKMESH = 1,
                TILEMAP = 2, CAMERA = 3,
                TRIGGER = 4, ENCOUNTER = 5,
                MODEL = 6, NUM_SECTIONS = 7)


# Field map data file
class MapData:

    # Parse the field map from an open file object.
    def __init__(self, fileobj):

        # Read the file data
        data = fileobj.read()

        # Decompress the file
        compressedSize = struct.unpack_from("<L", data)[0]
        data = lzss.decompress(data[4:4 + compressedSize])

        # Parse the pointer table
        numSections = 7
        tableSize = numSections * 4

        pointers = struct.unpack_from("<%dL" % numSections, data)

        self.basePointer = pointers[0]
        pointers += (self.basePointer + len(data) - tableSize, )  # dummy pointer to determine end of last section

        # Extract the section data (assumption: the pointers are in
        # ascending order, so the size of each section equals the difference
        # between adjacent pointers)
        self.sections = []
        for i in range(len(pointers) - 1):
            start = pointers[i] - self.basePointer + tableSize
            end = pointers[i + 1] - self.basePointer + tableSize
            assert end >= start

            self.sections.append(data[start:end])

    # Retrieve the event section data.
    def getEventSection(self):
        return EventSection(self.sections[Section.EVENT])

    # Replace the event section data.
    def setEventSection(self, event):
        data = event.getData()

        # Align section size to multiple of four
        if len(data) % 4:
            data.extend(b'\0' * (4 - len(data) % 4))

        self.sections[Section.EVENT] = data

    # Write the map to a file object, truncating the file.
    def writeToFile(self, fileobj):
        mapData = bytearray()

        # Create the pointer table
        pointer = self.basePointer
        for data in self.sections:
            mapData.extend(struct.pack("<L", pointer))
            pointer += len(data)

        # Append the sections
        for data in self.sections:
            mapData.extend(data)

        # Compress the map data
        cmpData = lzss.compress(mapData)

        # Write to file
        fileobj.seek(0)
        fileobj.truncate()
        fileobj.write(struct.pack("<L", len(cmpData)))
        fileobj.write(cmpData)


# Field map event section
class EventSection:

    # Create an EventSection object from binary data.
    def __init__(self, data):

        # Parse the section header
        headerSize = 32
        self.version, numActors, self.numModels, stringTableOffset, numExtra, self.scale, self.creator, self.mapName = struct.unpack_from("<HBBHHH6x8s8s", data)
        offset = headerSize

        self.creator = self.creator.rstrip(b'\0').decode(encoding = "sjis", errors = "backslashreplace")
        self.mapName = self.mapName.rstrip(b'\0').decode(encoding = "sjis", errors = "backslashreplace")

        # Read the actor names
        self.actorNames = []
        for i in range(numActors):
            name = struct.unpack_from("8s", data, offset)[0]
            offset += 8

            name = name.rstrip(b'\0').decode(encoding = "sjis", errors = "backslashreplace")
            self.actorNames.append(name)

        # Read the extra block (music/tutorial) offset table
        extraOffsets = []
        for i in range(numExtra):
            extraOffset = struct.unpack_from("<L", data, offset)[0]
            offset += 4

            extraOffsets.append(extraOffset)

        extraOffsets.append(len(data))  # dummy offset to determine end of last extra block

        # Read the actor script entry tables (32 entries per actor)
        self.actorScripts = []
        self.scriptEntryAddresses = set()
        for i in range(numActors):
            scripts = list(struct.unpack_from("<32H", data, offset))
            offset += 64

            self.actorScripts.append(scripts)
            self.scriptEntryAddresses |= set(scripts)

        # Read the script code (assumptions: the script data immediately
        # follows the actor script offset table, and the start of the string
        # table marks the end of the script data)
        self.scriptBaseAddress = offset
        self.scriptCode = bytearray(data[offset:stringTableOffset])

        if (len(self.scriptCode) + self.scriptBaseAddress) in self.scriptEntryAddresses:
            self.scriptCode.append(Op.RET)  # the SNW_W field has (unused) pointers after the end of the code

        # The default script of each actor continues after the first RET
        # instruction. In order to include the following code in control
        # flow analyses we add a 33rd element to each script entry table
        # which points to the instruction after the first RET of the
        # default script.
        for i in range(numActors):
            defaultScript = self.actorScripts[i][0]

            codeOffset = defaultScript - self.scriptBaseAddress

            while codeOffset < len(self.scriptCode):
                if self.scriptCode[codeOffset] == Op.RET:
                    entry = codeOffset + self.scriptBaseAddress + 1
                    self.actorScripts[i].append(entry)
                    self.scriptEntryAddresses.add(entry)
                    break
                else:
                    codeOffset += instructionSize(self.scriptCode, codeOffset)

        # Also look for double-RET instructions in regular scripts and
        # add pseudo entry points after them
        for i in range(numActors):
            for j in range(1, 32):
                codeOffset = self.actorScripts[i][j] - self.scriptBaseAddress

                while codeOffset < (len(self.scriptCode) - 2):
                    if self.scriptCode[codeOffset] == Op.RET and self.scriptCode[codeOffset + 1] == Op.RET:
                        entry = codeOffset + self.scriptBaseAddress + 2

                        if entry not in self.scriptEntryAddresses:
                            self.actorScripts[i].append(entry)
                            self.scriptEntryAddresses.add(entry)

                        codeOffset += 2
                    else:
                        codeOffset += instructionSize(self.scriptCode, codeOffset)

                        if (codeOffset + self.scriptBaseAddress) in self.scriptEntryAddresses:
                            break  # stop at next script

        # Read the string offset table
        offset = stringTableOffset
        offset += 2  # the first two bytes are supposed to indicate the number of strings, but this is totally unreliable
        firstOffset = struct.unpack_from("<H", data, offset)[0]
        numStrings = firstOffset // 2 - 1  # determine the number of strings by the first offset instead

        stringOffsets = []
        for i in range(numStrings):
            stringOffsets.append(struct.unpack_from("<H", data, offset)[0])
            offset += 2

        # Read the strings (assumption: each string is 0xff-terminated; we
        # don't use the offsets to calculate string sizes because the
        # strings may overlap, and the offsets may not be in ascending
        # order)
        self.stringData = []
        for o in stringOffsets:
            start = stringTableOffset + o
            end = data.find(b'\xff', start)
            self.stringData.append(data[start:end + 1])

        # Read the extra blocks (assumptions: offsets are in ascending order
        # and there is no other data between or after the extra blocks, so
        # the size of each block is the difference between adjacent offsets)
        self.extras = []
        for i in range(numExtra):
            start = extraOffsets[i]
            end = extraOffsets[i + 1]
            assert end >= start

            self.extras.append(data[start:end])

    # Return the list of all strings as unicode objects.
    def getStrings(self, japanese = False):
        return [ff7text.decodeField(s, japanese) for s in self.stringData]

    # Replace the entire string list.
    def setStrings(self, stringList, japanese = False):
        self.stringData = [ff7text.encode(s, True, japanese) for s in stringList]

    # Return the list of extra data blocks.
    def getExtras(self):
        return self.extras

    # Replace an extra data block.
    def setExtra(self, index, data):
        self.extras[index] = data

    # Encode event section to binary data and return it.
    def getData(self):
        version = 0x0502
        numActors = len(self.actorNames)
        numExtras = len(self.extras)
        numStrings = len(self.stringData)

        headerSize = 32
        actorNamesSize = numActors * 8
        extraOffsetsSize = numExtras * 4
        scriptTablesSize = numActors * 32 * 2
        scriptCodeSize = len(self.scriptCode)

        stringTableOffset = 32 + actorNamesSize + extraOffsetsSize + scriptTablesSize + scriptCodeSize

        # Create the string table
        stringOffsets = b""
        stringTable = b""

        offset = 2 + numStrings * 2
        for string in self.stringData:
            stringOffsets += struct.pack("<H", offset)
            stringTable += string
            offset += len(string)

        assert numStrings <= 256  # string IDs in MESSAGE/ASK/MPNAM commands are one byte only
        stringTable = struct.pack("<H", numStrings & 0xff) + stringOffsets + stringTable

        # Align string table size so the extra blocks are 32-bit aligned
        align = stringTableOffset + len(stringTable)
        if align % 4:
            stringTable += bytes([0]) * (4 - align % 4)

        stringTableSize = len(stringTable)

        # Write the header
        data = bytearray()
        data.extend(struct.pack("<HBBHHH6x8s8s", version, numActors, self.numModels, stringTableOffset, numExtras, self.scale, bytes(self.creator, "sjis"), bytes(self.mapName, "sjis")))

        # Write the actor names
        for name in self.actorNames:
            data.extend(struct.pack("8s", bytes(name, "sjis")))

        # Write the extra block offset table
        offset = stringTableOffset + stringTableSize
        for extra in self.extras:
            data.extend(struct.pack("<L", offset))
            offset += len(extra)

        # Write the actor script entry tables
        for scripts in self.actorScripts:
            for i in range(32):
                data.extend(struct.pack("<H", scripts[i]))

        # Write the script code
        data.extend(self.scriptCode)

        # Write the string table
        data.extend(stringTable)

        # Write the extra blocks
        for extra in self.extras:
            data.extend(extra)

        return data


# Mnemonic and operand length for each script opcode
opcodes = [
    # 0X00..0X07
    ("RET", 0),    ("REQ", 2),    ("REQSW", 2),  ("REQEW", 2),  ("PREQ", 2),   ("PRQSW", 2),  ("PRQEW", 2),  ("RETTO", 1),

    # 0X08..0X0F
    ("JOIN", 1),   ("SPLIT", 14), ("SPTYE", 5),  ("GPTYE", 5),  ("", -1),      ("", -1),      ("DSKCG", 1),  ("SPECIAL", 0),

    # 0X10..0X17
    ("JMPF", 1),   ("JMPFL", 2),  ("JMPB", 1),   ("JMPBL", 2),  ("IFUB", 5),     ("IFUBL", 6),    ("IFSW", 7),    ("IFSWL", 8),

    # 0X18..0X1F
    ("IFUW", 7),    ("IFUWL", 8),   ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),

    # 0X20..0X27
    ("MINIGAME", 10), ("TUTOR", 1),  ("BTMD2", 4),  ("BTRLD", 2),  ("WAIT", 2),   ("NFADE", 8),  ("BLINK", 1),  ("BGMOVIE", 1),

    # 0X28..0X2F
    ("KAWAI", 0),  ("KAWIW", 0),  ("PMOVA", 1),  ("SLIP", 1),   ("BGPDH", 4),  ("BGSCR", 6),  ("WCLS", 1),  ("WSIZW", 9),

    # 0X30..0X37
    ("IFKEY", 3),   ("IFKEYON", 3),  ("KEYOF", 3),  ("UC", 1),     ("PDIRA", 1),  ("PTURA", 3),  ("WSPCL", 4),  ("WNUMB", 7),

    # 0X38..0X3F
    ("STTIM", 5),  ("GOLDu", 5),  ("GOLDd", 5),  ("CHGLD", 3),  ("HMPMX1", 0),  ("HMPMX2", 0),  ("MHMMX", 0),  ("HMPMX3", 0),

    # 0X40..0X47
    ("MESSAGE", 2),    ("MPARA", 4),  ("MPRA2", 5),  ("MPNAM", 1),  ("", -1),      ("MPu", 4),    ("", -1),      ("MPd", 4),

    # 0X48..0X4F
    ("ASK", 6),    ("MENU", 3),   ("MENU2", 1),   ("BTLTB", 1),  ("", -1),      ("HPu", 4),    ("", -1),      ("HPd", 4),

    # 0X50..0X57
    ("WSIZE", 9),  ("WMOVE", 5),  ("WMODE", 3),  ("WREST", 1),  ("WCLSE", 1),  ("WROW", 2),   ("GWCOL", 6),  ("SWCOL", 6),

    # 0X58..0X5F
    ("STITM", 4),  ("DLITM", 4),  ("CKITM", 4),  ("SMTRA", 6),  ("DMTRA", 7),  ("CMTRA", 9),  ("SHAKE", 7),  ("WAIT", 0),

    # 0X60..0X67
    ("MAPJUMP", 9),  ("SCRLO", 1),  ("SCRLC", 4),  ("SCRLA", 5),  ("SCR2D", 5),  ("SCRCC", 0),  ("SCR2DC", 8), ("SCRLW", 0),

    # 0X68..0X6F
    ("SCR2DL", 8), ("MPDSP", 1),  ("VWOFT", 6),  ("FADE", 8),   ("FADEW", 0),  ("IDLCK", 3),  ("LSTMP", 2),  ("SCRLP", 5),

    # 0X70..0X77
    ("BATTLE", 3),  ("BTLON", 1),  ("BTLMD", 2),  ("PGTDR", 3),  ("GETPC", 3),  ("PXYZI", 7),  ("PLUS!", 3),  ("PLUS2!", 4),

    # 0X78..0X7F
    ("MINUS!", 3),  ("MINUS2!", 4),  ("INC!", 2),   ("INC2!", 2),  ("DEC!", 2),   ("DEC2!", 2),  ("TLKON", 1),  ("RDMSD", 2),

    # 0X80..0X87
    ("SETBYTE", 3),    ("SETWORD", 4),   ("BITON", 3),  ("BITOFF", 3),  ("BITXOR", 3),  ("PLUS", 3),   ("PLUS2", 4),  ("MINUS", 3),

    # 0X88..0X8F
    ("MINUS2", 4),  ("MUL", 3),    ("MUL2", 4),   ("DIV", 3),    ("DIV2", 4),   ("MOD", 3),  ("MOD2", 4),  ("AND", 3),

    # 0X90..0X97
    ("AND2", 4),   ("OR", 3),     ("OR2", 4),    ("XOR", 3),    ("XOR2", 4),   ("INC", 2),    ("INC2", 2),   ("DEC", 2),

    # 0X98..0X9F
    ("DEC2", 2),   ("RANDOM", 2),  ("LBYTE", 3),  ("HBYTE", 4),  ("2BYTE", 5),  ("SETX", 6),   ("GETX", 6),   ("SEARCHX", 10),

    # 0XA0..0XA7
    ("PC", 1),     ("CHAR", 1),   ("DFANM", 2),  ("ANIME1", 2),  ("VISI", 1),   ("XYZI", 10),  ("XYI", 8),    ("XYZ", 8),

    # 0XA8..0XAF
    ("MOVE", 5),   ("CMOVE", 5),  ("MOVA", 1),   ("TURA", 3),   ("ANIMW", 0),  ("FMOVE", 5),  ("ANIME2", 2),  ("ANIM!1", 2),

    # 0XB0..0XB7
    ("CANIM1", 4),  ("CANM!1", 4),  ("MSPED", 3),  ("DIR", 2),    ("TURNGEN", 5),  ("TURN", 5),   ("DIRA", 1),   ("GETDIR", 3),

    # 0XB8..0XBF
    ("GETAXY", 4), ("GETAI", 3),  ("ANIM!2", 2),  ("CANIM2", 4),  ("CANM!2", 4),  ("ASPED", 3),  ("", -1),      ("CC", 1),

    # 0XC0..0XC7
    ("JUMP", 10),  ("AXYZI", 7),  ("LADER", 14), ("OFST", 11), ("OFSTW", 0),  ("TALKR", 2),  ("SLIDR", 2),  ("SOLID", 1),

    # 0XC8..0XCF
    ("PRTYP", 1),  ("PRTYM", 1),  ("PRTYE", 3),  ("IFPRTYQ", 2),  ("IFMEMBQ", 2),  ("MMBud", 2),  ("MMBLK", 1),  ("MMBUK", 1),

    # 0XD0..0XD7
    ("LINE", 12),  ("LINON", 1),  ("MPJPO", 1),  ("SLINE", 15), ("SIN", 9),    ("COS", 9),    ("TLKR2", 3),  ("SLDR2", 3),

    # 0XD8..0XDF
    ("PMJUMP", 2),  ("PMJUMP2", 0),  ("AKAO2", 14), ("FCFIX", 1),  ("CCANM", 3),  ("ANIMB", 0),  ("TURNW", 0),  ("MPPAL", 10),

    # 0XE0..0XE7
    ("BGON", 3),   ("BGOFF", 3),  ("BGROL", 2),  ("BGROL2", 2),  ("BGCLR", 2),  ("STPAL", 4),  ("LDPAL", 4),  ("CPPAL", 4),

    # 0XE8..0XEF
    ("RTPAL", 6),  ("ADPAL", 9),  ("MPPAL2", 9),  ("STPLS", 4),  ("LDPLS", 4),  ("CPPAL2", 7),  ("RTPAL2", 7),  ("ADPAL2", 10),

    # 0XF0..0XF7
    ("MUSIC", 1),  ("SOUND", 4),     ("AKAO", 13),  ("MUSVT", 1),  ("MUSVM", 1),  ("MULCK", 1),  ("BMUSC", 1),  ("CHMPH", 3),

    # 0XF8..0XFF
    ("PMVIE", 1),  ("MOVIE", 0),  ("MVIEF", 2),  ("MVCAM", 1),  ("FMUSC", 1),  ("CMUSC", 5),  ("CHMST", 2),  ("GAMEOVER", 0),
]


# Mnemonic and operand length for SPECIAL sub-opcodes
specialOpcodes = {
    0xf5: ("ARROW", 1),
    0xf6: ("PNAME", 4),
    0xf7: ("GMSPD", 2),
    0xf8: ("SMSPD", 2),
    0xf9: ("FLMAT", 0),
    0xfa: ("FLITM", 0),
    0xfb: ("BTLCK", 1),
    0xfc: ("MVLCK", 1),
    0xfd: ("SPCNM", 2),
    0xfe: ("RSGLB", 0),
    0xff: ("CLITM", 0),
}


# Some selected opcodes (flow control and text/window-related)
Op = _enum(
    RET = 0x00, RETTO = 0x07, SPECIAL = 0x0f, JMPF = 0x10,
    JMPFL = 0x11, JMPB = 0x12, JMPBL = 0x13, IFUB = 0x14,
    IFUBL = 0x15, IFSW = 0x16, IFSWL = 0x17, IFUW = 0x18,
    IFUWL = 0x19, KAWAI = 0x28, WSIZW = 0x2f, IFKEY = 0x30,
    IFKEYON = 0x31, IFKEYOFF = 0x32, WSPCL = 0x36, MESSAGE = 0x40,
    MPNAM = 0x43, ASK = 0x48, WSIZE = 0x50, WREST = 0x53,
    IFPRTYQ = 0xcb, IFMEMBQ = 0xcc, GAMEOVER = 0xff,
    SPCNM = 0x0ffd,
)


#
# Terminology:
# - An "address" is the offset of a script instruction relative to the start
#   of the event section of the field map.
# - An "offset" refers to a relative location within the script code block,
#   and is used to refer to script code bytes within the bytearray which
#   holds the script code.
# - The "base address" of the script code block is the address of the script
#   instruction with offset 0.
#
# For example, if the script code block starts at byte 0x1234 within the
# event section, then the first instruction of the script is at address
# 0x1234, offset 0.
#


# Basic block of the control flow graph
class BasicBlock:
    def __init__(self):

        # List of offsets of the instructions which make up the block
        self.instructions = []

        # Set of addresses of succeeding blocks (zero for exit blocks,
        # one for sequential control flow or unconditional jumps, two
        # or more for conditional branches)
        self.succ = set()


# Find the size of the instruction at the given offset in a script code block.
def instructionSize(code, offset):
    op = code[offset]
    size = opcodes[op][1] + 1

    if op == Op.SPECIAL:

        # First operand byte is sub-opcode
        subOp = code[offset + 1]
        size = specialOpcodes[subOp][1] + 2

    elif op == Op.KAWAI:

        # Variable size given by first operand byte
        size = code[offset + 1]

    return size


# If the instruction at the given offset is a jump or branch instruction,
# return the jump target offset. Otherwise, return None.
def targetOffset(code, offset):
    op = code[offset]

    if op == Op.JMPF:
        return offset + code[offset + 1] + 1
    elif op == Op.JMPFL:
        return offset + (code[offset + 1] | (code[offset + 2] << 8)) + 1
    elif op == Op.JMPB:
        return offset - code[offset + 1]
    elif op == Op.JMPBL:
        return offset - (code[offset + 1] | (code[offset + 2] << 8))
    if op == Op.IFUB:
        return offset + code[offset + 5] + 5
    elif op == Op.IFUBL:
        return offset + (code[offset + 5] | (code[offset + 6] << 8)) + 5
    elif op in (Op.IFSW, Op.IFUW):
        return offset + code[offset + 7] + 7
    elif op in (Op.IFSWL, Op.IFUWL):
        return offset + (code[offset + 7] | (code[offset + 8] << 8)) + 7
    elif op in (Op.IFKEY, Op.IFKEYON, Op.IFKEYOFF):
        return offset + code[offset + 3] + 3
    elif op in (Op.IFPRTYQ, Op.IFMEMBQ):
        return offset + code[offset + 2] + 2
    else:
        return None


# Return true if the instruction at the given offset halts the control flow.
def isExit(code, offset):
    return code[offset] in (Op.RET, Op.RETTO, Op.GAMEOVER)

# Return true if the instruction at the given offset is an unconditional jump.
def isJump(code, offset):
    return code[offset] in (Op.JMPF, Op.JMPFL, Op.JMPB, Op.JMPBL)

# Return true if the instruction at the given offset is a conditional branch.
def isBranch(code, offset):
    return code[offset] in (Op.IFUB, Op.IFUBL, Op.IFSW, Op.IFSWL, Op.IFUW, Op.IFUWL,
                            Op.IFKEY, Op.IFKEYON, Op.IFKEYOFF, Op.IFPRTYQ, Op.IFMEMBQ)


# Build and return the control flow graph, a dictionary mapping addresses to
# BasicBlock objects.
def buildCFG(code, baseAddress, entryAddresses):

    # Find the addresses of the leaders, starting with the supplied set of
    # entry addresses
    leaders = set(entryAddresses)

    offset = 0
    while offset < len(code):
        nextOffset = offset + instructionSize(code, offset)

        # Instructions following exit points are leaders
        if isExit(code, offset):
            leaders.add(nextOffset + baseAddress)
        else:
            target = targetOffset(code, offset)

            # Targets of jump and branches, and the instructions following
            # a jump or branch, are leaders
            if target is not None:
                leaders.add(target + baseAddress)
                leaders.add(nextOffset + baseAddress)

        offset = nextOffset

    # For each leader, assemble the corresponding basic block, building
    # the graph
    graph = {}

    for leader in leaders:
        addr = leader
        offset = addr - baseAddress

        # If the last instruction of the code is a jump, there will be
        # a bogus leader pointing after the end of the code, which we
        # need to skip
        if offset >= len(code):
            continue

        block = BasicBlock()

        while True:

            # Append one instruction
            size = instructionSize(code, offset)
            block.instructions.append(offset)

            addr += size
            offset += size

            # Stop when reaching another leader, or before going outside the
            # code section
            if (addr in leaders) or (offset >= len(code)):
                break

        # Examine the last instruction of the block to determine the
        # block's successors
        assert len(block.instructions) > 0
        lastInstruction = block.instructions[-1]

        if isJump(code, lastInstruction):      # one successor: the jump target
            block.succ = set([targetOffset(code, lastInstruction) + baseAddress])
        elif isBranch(code, lastInstruction):  # two successors: the branch target and the next instruction
            if offset >= len(code):
                raise IndexError("Control flow reaches end of script code")
            block.succ = set([targetOffset(code, lastInstruction) + baseAddress, addr])
        elif isExit(code, lastInstruction):    # no successors
            block.succ = set()
        else:                                  # one successor: the next instruction
            if offset >= len(code):
                raise IndexError("Control flow reaches end of script code")
            block.succ = set([addr])

        # Add the block to the graph
        graph[leader] = block

    return graph


# Determine all possible paths through a control flow graph starting at a given
# entry point, ignoring any cycles.
#
# This function returns a list of paths, each path being a list of instruction
# addresses.
def findPaths(graph, entryAddress, path = []):
    path = path + [entryAddress]

    succ = graph[entryAddress].succ
    if not succ:
        return [path]  # exit reached

    paths = []
    for addr in succ:
        if addr not in path:
            paths += findPaths(graph, addr, path)

    if paths:
        return paths
    else:
        return [path]  # cycle reached


# Remove instructions from the blocks of a code flow graph, only keeping those
# in the specified list. The passed-in graph is modified by this function.
# SPECIAL 2-byte opcodes which should be kept can be specified as 0x0fxx.
def filterInstructions(graph, code, keep):
    for block in list(graph.values()):
        newInstructions = []

        for offset in block.instructions:
            op = code[offset]
            if op == Op.SPECIAL:
                op = (op << 8) | code[offset + 1]

            if op in keep:
                newInstructions.append(offset)

        block.instructions = newInstructions


# Recursively find all possible exits from a given block which lie
# outside of a specified address range.
def possibleExitsFrom(graph, block, minAddr, maxAddr, consideredBlocks = set()):
    exits = set()

    if block in consideredBlocks:
        return exits
    else:
        consideredBlocks.add(block)

    for succ in block.succ:
        if succ >= minAddr and succ < maxAddr:
            exits |= possibleExitsFrom(graph, graph[succ], minAddr, maxAddr, consideredBlocks)
        else:
            exits.add(succ)

    return exits


# Reduce a (filtered) graph in order to lower the number of paths to examine
# for cases where we're only interested in the possible sequence of
# instructions. The passed-in graph is modified by this function.
def reduce(graph, entryAddresses):

    while True:
        nothingChanged = True

        # Eliminate the condition from simple 'if c then b' constructs by
        # assuming that the inner block is always executed
        for blockAddr, block in graph.items():
            if len(block.succ) == 2:
                sortedSuccs = sorted(list(block.succ))
                innerAddr = sortedSuccs[0]
                exitAddr = sortedSuccs[1]

                innerBlock = graph[innerAddr]
                if possibleExitsFrom(graph, innerBlock, innerAddr, exitAddr) == set([exitAddr]):
#                    print "eliminating %s -> %04x" % (map(hex, list(block.succ)), innerAddr)
                    block.succ = set([innerAddr])
                    nothingChanged = False

        if nothingChanged:
            break
                
    while True:
        nothingChanged = True

        # Skip blocks with no (filtered) instructions as long as it reduces
        # the number of paths
        for blockAddr, block in graph.items():
            newSucc = set()

            for addr in block.succ:
                succBlock = graph[addr]
                if not succBlock.instructions:
                    newSucc |= succBlock.succ
                else:
                    newSucc |= set([addr])

            newSucc.discard(blockAddr)  # remove simple cycles

            if newSucc != block.succ and len(newSucc) < 3:  # avoid excessive branching
#                print "reducing %s -> %s" % (map(hex, list(block.succ)), map(hex, list(newSucc)))
                block.succ = newSucc
                nothingChanged = False

        if nothingChanged:
            break

    while True:
        nothingChanged = True

        # Remove orphaned blocks
        referencedBlocks = set(entryAddresses)
        for block in list(graph.values()):
            referencedBlocks |= block.succ

        for addr in list(graph.keys())[:]:
            if addr not in referencedBlocks:
#                print "deleting %04x" % addr
                del graph[addr]
                nothingChanged = False

        if nothingChanged:
            break


# Dissasemble script code, optionally printing labels before instructions.
# The 'baseAddress' specifies the (virtual) start address of the first
# script instruction.
def disassemble(code, baseAddress = 0, labels = []):
    s = ""

    offset = 0
    while offset < len(code):
        addr = offset + baseAddress

        firstLabel = True
        for labelText, labelOffset in labels:
            if labelOffset == addr:
                if firstLabel:
                    s += '\n'
                    firstLabel = False

                s += "%s:" % labelText
                s += '\n'

        format = "%04x: "
        values = (addr, )

        op = code[offset]
        offset += 1

        mnemonic, size = opcodes[op]

        if op == Op.SPECIAL:  # first operand byte is sub-opcode
            subOp = code[offset]
            offset += 1
            mnemonic, size = specialOpcodes[subOp]
        elif op == Op.KAWAI:  # variable size given by first operand byte
            size = code[offset] - 1

        if size < 0:  # illegal opcode
            mnemonic = "<%02x>" % op
            size = 0

        format += "%s"
        values += (mnemonic, )
        for i in range(offset, offset + size):
            format += " %02x"
            values += (code[i], )

        s += format % values
        s += '\n'

        offset += size

    return s
