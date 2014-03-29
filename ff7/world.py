#
# ff7.world - Final Fantasy VII world event script handling
#
# Copyright (C) 2014 Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct

import lzss


def _enum(**enums):
    return type('Enum', (), enums)


# Some selected opcodes
Op = _enum(
    CLEAR = 0x100,
    PUSHI = 0x110,
    JUMP = 0x200,
    JUMPZ = 0x201,
    WINDOW = 0x324,
    MES = 0x325,
    ASK = 0x326
)


# Find the size (number of 16-bit values) of the given instruction.
def instructionSize(op):
    if op > 0x100 and op < 0x200:  # push
        return 2
    elif op in [Op.JUMP, Op.JUMPZ]:  # jump
        return 2
    else:
        return 1


# World map file
class WorldMap:

    # Parse the map from an open file object.
    def __init__(self, fileobj):

        # Read the file data
        cmpData = fileobj.read()

        # Decompress the file
        compressedSize = struct.unpack_from("<L", cmpData)[0]
        self.data = bytearray(lzss.decompress(cmpData[4:4 + compressedSize]))

        # Find the script section
        offset = struct.unpack_from("<L", self.data, 0x14)[0]
        size = struct.unpack_from("<L", self.data, 0x18)[0] - offset

        self.scriptStart = offset + 4
        self.scriptEnd = self.scriptStart + size

    # Return the script code as a list of 16-bit values.
    def getScript(self):
        script = []

        # Convert code after the entry table until we find a
        # null opcode or reach the end of the data
        offset = self.scriptStart + 0x400
        while offset < self.scriptEnd:
            op = struct.unpack_from("<H", self.data, offset)[0]
            offset += 2

            if op == 0:
                break

            script.append(op)

            for i in xrange(instructionSize(op) - 1):
                script.append(struct.unpack_from("<H", self.data, offset)[0])
                offset += 2

        return script

    # Insert script code back into the data.
    def setScript(self, script):
        offset = self.scriptStart + 0x400
        for w in script:
            struct.pack_into("<H", self.data, offset, w)
            offset += 2

    # Write the map to a file object, truncating the file.
    def writeToFile(self, fileobj):

        # Compress the map data
        cmpData = lzss.compress(str(self.data))

        # Write to file
        fileobj.seek(0)
        fileobj.truncate()
        fileobj.write(struct.pack("<L", len(cmpData)))
        fileobj.write(cmpData)


# Map opcodes to mnemonics
opcodes = {
    0x015: "neg",
    0x017: "not",
    0x030: "*",
    0x040: "+",
    0x041: "-",
    0x050: "<<",
    0x051: ">>",
    0x060: "<",
    0x061: ">",
    0x062: "<=",
    0x063: ">=",
    0x070: "==",
    0x071: "!=",
    0x080: "&",
    0x0a0: "|",
    0x0b0: "&&",
    0x0c0: "||",
    0x0e0: "store",
    0x100: "clear",
    0x200: "jump",
    0x201: "jumpz",
    0x203: "return",
    0x324: "window",
    0x325: "mes",
    0x326: "ask"
}


# Disassemble script code.
def disassemble(script):
    s = ""

    i = 0
    while i < len(script):
        s += "%04x: " % i

        op = script[i]
        i += 1

        if op == Op.PUSHI:
            s += "push #%04x" % script[i]
            i += 1
        elif op in [0x114, 0x115, 0x116]:
            s += "push bit %d/%04x" % (op & 3, script[i])
            i += 1
        elif op in [0x118, 0x119, 0x11a]:
            s += "push byte %d/%04x" % (op & 3, script[i])
            i += 1
        elif op in [0x11c, 0x11d, 0x11e]:
            s += "push halfword %d/%04x" % (op & 3, script[i])
            i += 1
        elif op > 0x100 and op < 0x200 and op & 3 == 3:
            s += "push special %04x" % script[i]
            i += 1
        elif op == Op.JUMP:
            s += "%s %04x" % (opcodes[op], script[i])
            i += 1
        elif op == Op.JUMPZ:
            s += "%s %04x" % (opcodes[op], script[i])
            i += 1
        elif op > 0x203 and op < 0x300:
            s += "exec %03x" % op
        else:
            try:
                s += opcodes[op]
            except KeyError:
                s += "<%04x>" % op

        s += "\n"

    return s
