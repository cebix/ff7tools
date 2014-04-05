#
# ff7.field - Final Fantasy VII field map and script handling
#
# Copyright (C) 2014 Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct

import lzss
import ff7text


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
        for i in xrange(len(pointers) - 1):
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
            data += '\0' * (4 - len(data) % 4)

        self.sections[Section.EVENT] = data

    # Write the map to a file object, truncating the file.
    def writeToFile(self, fileobj):
        mapData = ""

        # Create the pointer table
        pointer = self.basePointer
        for data in self.sections:
            mapData += struct.pack("<L", pointer)
            pointer += len(data)

        # Append the sections
        for data in self.sections:
            mapData += data

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

        self.creator = self.creator.rstrip('\0')
        self.mapName = self.mapName.rstrip('\0')

        # Read the actor names
        self.actorNames = []
        for i in xrange(numActors):
            name = struct.unpack_from("8s", data, offset)[0]
            offset += 8

            name = name.rstrip('\0')
            self.actorNames.append(name)

        # Read the extra block (music/tutorial) offset table
        extraOffsets = []
        for i in xrange(numExtra):
            extraOffset = struct.unpack_from("<L", data, offset)[0]
            offset += 4

            extraOffsets.append(extraOffset)

        extraOffsets.append(len(data))  # dummy offset to determine end of last extra block

        # Read the actor script entry tables (32 entries per actor)
        self.actorScripts = []
        self.scriptEntryAddresses = set()
        for i in xrange(numActors):
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
        for i in xrange(numActors):
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
        for i in xrange(numActors):
            for j in xrange(1, 32):
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
        numStrings = firstOffset / 2 - 1  # determine the number of strings by the first offset instead

        stringOffsets = []
        for i in xrange(numStrings):
            stringOffsets.append(struct.unpack_from("<H", data, offset)[0])
            offset += 2

        # Read the strings (assumption: each string is 0xff-terminated; we
        # don't use the offsets to calculate string sizes because the
        # strings may overlap, and the offsets may not be in ascending
        # order)
        self.stringData = []
        for o in stringOffsets:
            start = stringTableOffset + o
            end = data.find('\xff', start)
            self.stringData.append(data[start:end + 1])

        # Read the extra blocks (assumptions: offsets are in ascending order
        # and there is no other data between or after the extra blocks, so
        # the size of each block is the difference between adjacent offsets)
        self.extras = []
        for i in xrange(numExtra):
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
        stringOffsets = ""
        stringTable = ""

        offset = 2 + numStrings * 2
        for string in self.stringData:
            stringOffsets += struct.pack("<H", offset)
            stringTable += string
            offset += len(string)

        assert numStrings <= 256  # string IDs in MES/ASK/MPNAM commands are one byte only
        stringTable = struct.pack("<H", numStrings & 0xff) + stringOffsets + stringTable

        # Align string table size so the extra blocks are 32-bit aligned
        align = stringTableOffset + len(stringTable)
        if align % 4:
            stringTable += '\0' * (4 - align % 4)

        stringTableSize = len(stringTable)

        # Write the header
        data = struct.pack("<HBBHHH6x8s8s", version, numActors, self.numModels, stringTableOffset, numExtras, self.scale, self.creator, self.mapName)

        # Write the actor names
        for name in self.actorNames:
            data += struct.pack("8s", name)

        # Write the extra block offset table
        offset = stringTableOffset + stringTableSize
        for extra in self.extras:
            data += struct.pack("<L", offset)
            offset += len(extra)

        # Write the actor script entry tables
        for scripts in self.actorScripts:
            for i in xrange(32):
                data += struct.pack("<H", scripts[i])

        # Write the script code
        data += str(self.scriptCode)

        # Write the string table
        data += stringTable

        # Write the extra blocks
        for extra in self.extras:
            data += extra

        return data


# Mnemonic and operand length for each script opcode
opcodes = [
    # 0x00..0x07
    ("ret", 0),    ("req", 2),    ("reqsw", 2),  ("reqew", 2),  ("preq", 2),   ("prqsw", 2),  ("prqew", 2),  ("retto", 1),

    # 0x08..0x0f
    ("join", 1),   ("split", 14), ("sptye", 5),  ("gptye", 5),  ("", -1),      ("", -1),      ("dskcg", 1),  ("spcal", 0),

    # 0x10..0x17
    ("skip", 1),   ("lskip", 2),  ("back", 1),   ("lback", 2),  ("if", 5),     ("lif", 6),    ("if2", 7),    ("lif2", 8),

    # 0x18..0x1f
    ("if2", 7),    ("lif2", 8),   ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),

    # 0x20..0x27
    ("mgame", 10), ("tutor", 1),  ("btmd2", 4),  ("btrlt", 2),  ("wait", 2),   ("nfade", 8),  ("blink", 1),  ("bgmovie", 1),

    # 0x28..0x2f
    ("kawai", 0),  ("kawiw", 0),  ("pmova", 1),  ("slip", 1),   ("bgdph", 4),  ("bgscr", 6),  ("wcls!", 1),  ("wsizw", 9),

    # 0x30..0x37
    ("key!", 3),   ("keyon", 3),  ("keyof", 3),  ("uc", 1),     ("pdira", 1),  ("ptura", 3),  ("wspcl", 4),  ("wnumb", 7),

    # 0x38..0x3f
    ("sttim", 5),  ("gold+", 5),  ("gold-", 5),  ("chgld", 3),  ("hmpmx", 0),  ("hmpmx", 0),  ("mhmmx", 0),  ("hmpmx", 0),

    # 0x40..0x47
    ("mes", 2),    ("mpara", 4),  ("mpra2", 5),  ("mpnam", 1),  ("", -1),      ("mp+", 4),    ("", -1),      ("mp-", 4),

    # 0x48..0x4f
    ("ask", 6),    ("menu", 3),   ("menu", 1),   ("btltb", 1),  ("", -1),      ("hp+", 4),    ("", -1),      ("hp-", 4),

    # 0x50..0x57
    ("wsize", 9),  ("wmove", 5),  ("wmode", 3),  ("wrest", 1),  ("wclse", 1),  ("wrow", 2),   ("gwcol", 6),  ("swcol", 6),

    # 0x58..0x5f
    ("stitm", 4),  ("dlitm", 4),  ("ckitm", 4),  ("smtra", 6),  ("dmtra", 7),  ("cmtra", 9),  ("shake", 7),  ("wait", 0),

    # 0x60..0x67
    ("mjump", 9),  ("scrlo", 1),  ("scrlc", 4),  ("scrla", 5),  ("scr2d", 5),  ("scrcc", 0),  ("scr2dc", 8), ("scrlw", 0),

    # 0x68..0x6f
    ("scr2dl", 8), ("mpdsp", 1),  ("vwoft", 6),  ("fade", 8),   ("fadew", 0),  ("idlck", 3),  ("lstmp", 2),  ("scrlp", 5),

    # 0x70..0x77
    ("batle", 3),  ("btlon", 1),  ("btlmd", 2),  ("pgtdr", 3),  ("getpc", 3),  ("pxyzi", 7),  ("plus!", 3),  ("pls2!", 4),

    # 0x78..0x7f
    ("mins!", 3),  ("mns2!", 4),  ("inc!", 2),   ("inc2!", 2),  ("dec!", 2),   ("dec2!", 2),  ("tlkon", 1),  ("rdmsd", 2),

    # 0x80..0x87
    ("set", 3),    ("set2", 4),   ("biton", 3),  ("bitof", 3),  ("bitxr", 3),  ("plus", 3),   ("plus2", 4),  ("minus", 3),

    # 0x88..0x8f
    ("mins2", 4),  ("mul", 3),    ("mul2", 4),   ("div", 3),    ("div2", 4),   ("remai", 3),  ("rema2", 4),  ("and", 3),

    # 0x90..0x97
    ("and2", 4),   ("or", 3),     ("or2", 4),    ("xor", 3),    ("xor2", 4),   ("inc", 2),    ("inc2", 2),   ("dec", 2),

    # 0x98..0x9f
    ("dec2", 2),   ("randm", 2),  ("lbyte", 3),  ("hbyte", 4),  ("2byte", 5),  ("setx", 6),   ("getx", 6),   ("srchx", 10),

    # 0xa0..0xa7
    ("pc", 1),     ("char", 1),   ("dfanm", 2),  ("anime", 2),  ("visi", 1),   ("xyzi", 10),  ("xyi", 8),    ("xyz", 8),

    # 0xa8..0xaf
    ("move", 5),   ("cmove", 5),  ("mova", 1),   ("tura", 3),   ("animw", 0),  ("fmove", 5),  ("anime", 2),  ("anim!", 2),

    # 0xb0..0xb7
    ("canim", 4),  ("canm!", 4),  ("msped", 3),  ("dir", 2),    ("turnr", 5),  ("turn", 5),   ("dira", 1),   ("gtdir", 3),

    # 0xb8..0xbf
    ("getaxy", 4), ("getai", 3),  ("anim!", 2),  ("canim", 4),  ("canm!", 4),  ("asped", 3),  ("", -1),      ("cc", 1),

    # 0xc0..0xc7
    ("jump", 10),  ("axyzi", 7),  ("lader", 14), ("ofstd", 11), ("ofstw", 0),  ("talkR", 2),  ("slidR", 2),  ("solid", 1),

    # 0xc8..0xcf
    ("prtyp", 1),  ("prtym", 1),  ("prtye", 3),  ("prtyq", 2),  ("membq", 2),  ("mmb+-", 2),  ("mmblk", 1),  ("mmbuk", 1),

    # 0xd0..0xd7
    ("line", 12),  ("linon", 1),  ("mpjpo", 1),  ("sline", 15), ("sin", 9),    ("cos", 9),    ("tlkR2", 3),  ("sldR2", 3),

    # 0xd8..0xdf
    ("pmjmp", 2),  ("pmjmp", 0),  ("akao2", 14), ("fcfix", 1),  ("ccanm", 3),  ("animb", 0),  ("turnw", 0),  ("mppal", 10),

    # 0xe0..0xe7
    ("bgon", 3),   ("bgoff", 3),  ("bgrol", 2),  ("bgrol", 2),  ("bgclr", 2),  ("stpal", 4),  ("ldpal", 4),  ("cppal", 4),

    # 0xe8..0xef
    ("rtpal", 6),  ("adpal", 9),  ("mppal", 9),  ("stpls", 4),  ("ldpls", 4),  ("cppal", 7),  ("rtpal", 7),  ("adpal", 10),

    # 0xf0..0xf7
    ("music", 1),  ("se", 4),     ("akao", 13),  ("musvt", 1),  ("musvm", 1),  ("mulck", 1),  ("bmusc", 1),  ("chmph", 3),

    # 0xf8..0xff
    ("pmvie", 1),  ("movie", 0),  ("mvief", 2),  ("mvcam", 1),  ("fmusc", 1),  ("cmusc", 5),  ("chmst", 2),  ("gmovr", 0),
]


# Mnemonic and operand length for SPCAL sub-opcodes
specialOpcodes = {
    0xf5: ("arrow", 1),
    0xf6: ("pname", 4),
    0xf7: ("gmspd", 2),
    0xf8: ("smspd", 2),
    0xf9: ("flmat", 0),
    0xfa: ("flitm", 0),
    0xfb: ("btlck", 1),
    0xfc: ("mvlck", 1),
    0xfd: ("spcnm", 2),
    0xfe: ("rsglb", 0),
    0xff: ("clitm", 0),
}


# Some selected opcodes (flow control and text/window-related)
Op = _enum(
    RET = 0x00, RETTO = 0x07, SPCAL = 0x0f, SKIP = 0x10,
    LSKIP = 0x11, BACK = 0x12, LBACK = 0x13, IF = 0x14,
    LIF = 0x15, IF2 = 0x16, LIF2 = 0x17, IF2U = 0x18,
    LIF2U = 0x19, KAWAI = 0x28, WSIZW = 0x2f, KEYQ = 0x30,
    KEYON = 0x31, KEYOFF = 0x32, WSPCL = 0x36, MES = 0x40,
    MPNAM = 0x43, ASK = 0x48, WSIZE = 0x50, WREST = 0x53,
    PRTYQ = 0xcb, MEMBQ = 0xcc, GMOVR = 0xff,
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

    if op == Op.SPCAL:

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

    if op == Op.SKIP:
        return offset + code[offset + 1] + 1
    elif op == Op.LSKIP:
        return offset + (code[offset + 1] | (code[offset + 2] << 8)) + 1
    elif op == Op.BACK:
        return offset - code[offset + 1]
    elif op == Op.LBACK:
        return offset - (code[offset + 1] | (code[offset + 2] << 8))
    if op == Op.IF:
        return offset + code[offset + 5] + 5
    elif op == Op.LIF:
        return offset + (code[offset + 5] | (code[offset + 6] << 8)) + 5
    elif op in (Op.IF2, Op.IF2U):
        return offset + code[offset + 7] + 7
    elif op in (Op.LIF2, Op.LIF2U):
        return offset + (code[offset + 7] | (code[offset + 8] << 8)) + 7
    elif op in (Op.KEYQ, Op.KEYON, Op.KEYOFF):
        return offset + code[offset + 3] + 3
    elif op in (Op.PRTYQ, Op.MEMBQ):
        return offset + code[offset + 2] + 2
    else:
        return None


# Return true if the instruction at the given offset halts the control flow.
def isExit(code, offset):
    return code[offset] in (Op.RET, Op.RETTO, Op.GMOVR)

# Return true if the instruction at the given offset is an unconditional jump.
def isJump(code, offset):
    return code[offset] in (Op.SKIP, Op.LSKIP, Op.BACK, Op.LBACK)

# Return true if the instruction at the given offset is a conditional branch.
def isBranch(code, offset):
    return code[offset] in (Op.IF, Op.LIF, Op.IF2, Op.LIF2, Op.IF2U, Op.LIF2U,
                            Op.KEYQ, Op.KEYON, Op.KEYOFF, Op.PRTYQ, Op.MEMBQ)


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
                raise IndexError, "Control flow reaches end of script code"
            block.succ = set([targetOffset(code, lastInstruction) + baseAddress, addr])
        elif isExit(code, lastInstruction):    # no successors
            block.succ = set()
        else:                                  # one successor: the next instruction
            if offset >= len(code):
                raise IndexError, "Control flow reaches end of script code"
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
# SPCAL 2-byte opcodes which should be kept can be specified as 0x0fxx.
def filterInstructions(graph, code, keep):
    for block in graph.values():
        newInstructions = []

        for offset in block.instructions:
            op = code[offset]
            if op == Op.SPCAL:
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
        for blockAddr, block in graph.iteritems():
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
        for blockAddr, block in graph.iteritems():
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
        for block in graph.values():
            referencedBlocks |= block.succ

        for addr in graph.keys()[:]:
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

        if op == Op.SPCAL:  # first operand byte is sub-opcode
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
