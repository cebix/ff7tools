#
# ff7.tutorial - Final Fantasy VII tutorial handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import sys
import struct
import re

from . import ff7text


# Tutorial script opcodes
opcodes = {
    # 0x00 - {WAIT <arg>}
    0x02: "{UP}",
    0x03: "{DOWN}",
    0x04: "{LEFT}",
    0x05: "{RIGHT}",
    0x06: "{MENU}",
    0x07: "{CANCEL}",
    0x09: "{OK}",
    0x0a: "{PREV}",
    0x0c: "{NEXT}",
    # 0x10 - text
    # 0x11 - end of script
    # 0x12 - {WINDOW <x> <y>}
}

# Inverse mapping of tutorial commands to opcodes
commands = {v:k for k, v in opcodes.items() if v}


# Tutorial script
class Script:

    # Create tutorial object from binary data.
    def __init__(self, data):
        self.data = data

    # Return binary tutorial data.
    def getData(self):
        return self.data

    # Disassemble tutorial script to list of strings.
    def getScript(self, japanese = False):
        data = self.data
        dataSize = len(data)
        script = []

        i = 0
        while i < dataSize:
            c = data[i]
            i += 1

            if c == 0x11:

                # End of script
                break

            elif c == 0x00:

                # WAIT <arg>
                if i >= dataSize - 1:
                    raise IndexError("Spurious WAIT command in tutorial data")

                arg = struct.unpack_from("<H", data, i)
                i += 2

                script.append("{WAIT %d}" % arg)

            elif c == 0x10:

                # Text string
                end = data.index(b'\xff', i)
                script.append(ff7text.decodeKernel(data[i:end], japanese))
                i = end + 1

            elif c == 0x12:

                # WINDOW <x> <y>
                if i >= dataSize - 3:
                    raise IndexError("Spurious WINDOW command in tutorial data")

                x, y = struct.unpack_from("<HH", data, i)
                i += 4

                script.append("{WINDOW %d %d}" % (x, y))

            else:

                # Other opcode
                if c in opcodes:
                    script.append(opcodes[c])
                else:
                    raise IndexError("Illegal opcode %02x in tutorial data" % c)

        return script

    # Assemble tutorial data from list of strings.
    def setScript(self, script, japanese = False):
        data = bytearray()

        for line in script:
            if line.startswith( "{WAIT" ):

                # WAIT <arg>
                m = re.match(r"{WAIT (\d+)}", line)
                if not m:
                    raise ValueError("Syntax error in command '%s' in tutorial script" % line)

                arg = int(m.group(1))
                if arg > 0xffff:
                    raise ValueError("Argument of WAIT command greater than 65535 in tutorial script")

                data.append(0)
                data.extend(struct.pack("<H", arg))

            elif line.startswith( "{WINDOW" ):

                # WINDOW <x> <y>
                m = re.match(r"{WINDOW (\d+) (\d+)}", line)
                if not m:
                    raise ValueError("Syntax error in command '%s' in tutorial script" % line)

                x = int(m.group(1))
                y = int(m.group(2))
                if x > 0xffff:
                    raise ValueError("First argument of WINDOW command greater than 65535 in tutorial script")
                if y > 0xffff:
                    raise ValueError("Second argument of WINDOW command greater than 65535 in tutorial script")

                data.append(0x12)
                data.extend(struct.pack("<HH", x, y))

            elif line.startswith( "{" ):

                # Simple command without arguments
                try:
                    code = commands[line]
                    data.append(code)
                except KeyError:
                    raise ValueError("Unknown command '%s' in tutorial script" % line)

            else:

                # Text line
                data.append(0x10)
                data.extend(ff7text.encode(line, False, japanese))

        data.append(0x11)  # end of script
        self.data = data
