#
# ff7.scene - Final Fantasy VII battle scene handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct
import gzip
import io

import ff7


def _enum(**enums):
    return type('Enum', (), enums)


# Some selected opcodes (control flow and text handling)
Op = _enum(
    JMPZ = 0x70,
    JMPNE = 0x71,
    JMP = 0x72,
    MES = 0x93,
    DEBUG = 0xa0,
)


class Instruction:

    # Create an instruction from binary data at a given offset
    def __init__(self, data, offset):
        self.offset = offset

        op = data[offset]
        self.op = op

        size = 1
        if op == 0x60:
            size = 2
        elif op == 0x61:
            size = 3
        elif op == 0x62:
            size = 4
        elif op in [0x00, 0x01, 0x02, 0x03, 0x10, 0x11, 0x12, 0x13, Op.JMPZ, Op.JMPNE, Op.JMP]:
            size = 3
        elif op == Op.MES:
            i = offset
            while data[i] != 0xff:  # 0xff-terminated
                i += 1
            size = i + 1 - offset
        elif op == Op.DEBUG:
            i = offset + 1
            while data[i] != 0x00:  # 0x00-terminated
                i += 1
            size = i + 1 - offset

        self.size = size
        self.code = data[offset:offset + size]

    def __str__(self):
        return "%04x: " % self.offset + ", ".join(map(hex, self.code))

    def setOffset(self, offset):
        self.offset = offset

    def setArg(self, arg):
        self.code = bytearray([self.op]) + bytearray(arg)
        self.size = len(self.code)


# Decode binary script data, returning a list of Instruction objects.
def decodeScript(data):
    instructions = []

    offset = 0
    while offset < len(data):
        instr = Instruction(data, offset)
        instructions.append(instr)
        offset += instr.size

    return instructions


# Battle scene
class Scene:
    def __init__(self, data, index):
        self.data = data
        self.index = index

        if len(data) == 0x1c50:

            # Old scene format (original Japanese version)
            self.maxStringSize = 0x10
            self.enemyDataOffset = 0x298
            self.enemyDataSize = 0xa8
            self.abilitiesOffset = 0x850
            self.aiDataOffset = 0xc50

        elif len(data) == 0x1e80:

            # New scene format
            self.maxStringSize = 0x20
            self.enemyDataOffset = 0x298
            self.enemyDataSize = 0xb8
            self.abilitiesOffset = 0x880
            self.aiDataOffset = 0xe80

        else:
            raise EnvironmentError("Battle scene %d has unexpected length" % index)

        # Extract enemy scripts
        self.enemyScripts = self.extractScripts(self.aiDataOffset, 3, len(data))

    # Return the binary scene data
    def getData(self):
        return self.data

    # Extract entity scripts from binary scene data.
    # Returns a list of numEntities lists of 16 scripts, each script being a
    # list of Instruction objects.
    def extractScripts(self, entitiesOffset, numEntities, maxOffset):
        scripts = []

        # Process all entities
        entitiesTable = struct.unpack_from("<%dH" % numEntities, self.data, entitiesOffset)

        for i in range(numEntities):
            offset = entitiesTable[i]

            if offset == 0xffff:
                scripts.append(None)  # no entity
            else:
                scriptsOfEntity = []

                # Fetch the entity's script table
                tableOffset = entitiesOffset + offset
                scriptsTable = struct.unpack_from("<16H", self.data, tableOffset)

                # The start of the next entity's table (or the end of the
                # data) is the upper offset limit for scripts of this entity
                nextTableOffset = maxOffset
                for j in range(i + 1, numEntities):
                    if entitiesTable[j] != 0xffff:
                        nextTableOffset = entitiesOffset + entitiesTable[j]
                        break

                # Process all scripts in the script table
                for j in range(16):
                    offset = scriptsTable[j]

                    if offset == 0xffff:
                        scriptsOfEntity.append(None)  # no script
                    else:
                        scriptOffset = tableOffset + offset

                        # The start of the next script (or the start of the
                        # next entity's script table) is the upper offset
                        # limit for the script
                        nextScriptOffset = nextTableOffset
                        for k in range(j + 1, 16):
                            if scriptsTable[k] != 0xffff:
                                nextScriptOffset = tableOffset + scriptsTable[k]
                                break

                        # Fetch the script data
                        scriptData = self.data[scriptOffset:nextScriptOffset]

                        # Remove trailing 0xff bytes
                        while scriptData[-1] == 0xff:
                            scriptData = scriptData[:-1]

                        scriptsOfEntity.append(decodeScript(bytearray(scriptData)))

                scripts.append(scriptsOfEntity)

        return scripts

    # Insert list of entity scripts into binary scene data.
    def insertScripts(self, scripts, entitiesOffset, numEntities, maxOffset):
        entityTable = []
        entityData = bytearray()
        tableOffset = numEntities * 2

        for i in range(numEntities):
            scriptsOfEntity = scripts[i]

            if scriptsOfEntity is None:
                entityTable.append(0xffff)  # no entity
            else:
                scriptsTable = []
                scriptData = bytearray()
                scriptOffset = 32

                for j in range(16):
                    script = scriptsOfEntity[j]
                    if script is None:
                        scriptsTable.append(0xffff)  # no script
                    else:
                        code = b"".join([i.code for i in script])
                        scriptData.extend(code)

                        scriptsTable.append(scriptOffset)
                        scriptOffset += len(code)

                if len(scriptData) % 2:
                    scriptData.append(0xff)  # align to 16-bit boundary
                    scriptOffset += 1

                # Append scripts table and all script data to entity data
                for offset in scriptsTable:
                    entityData.extend(struct.pack("<H", offset))

                entityData.extend(scriptData)

                entityTable.append(tableOffset)
                tableOffset += scriptOffset

        # Construct entity table and insert into scene data together with
        # entity data
        insertData = bytearray()
        for offset in entityTable:
            insertData.extend(struct.pack("<H", offset))
        insertData.extend(entityData)

        targetSize = maxOffset - entitiesOffset
        assert len(insertData) <= targetSize

        if len(insertData) < targetSize:
            insertData.extend(bytes([0xff] * (targetSize - len(insertData))))  # pad with 0xff bytes

        prevDataSize = len(self.data)

        self.data = self.data[:entitiesOffset] + insertData + self.data[maxOffset:]
        assert len(self.data) == prevDataSize

    # Return the enemy names defined in the scene.
    def getEnemyNames(self, japanese = False):
        enemies = []

        for i in range(3):
            offset = self.enemyDataOffset + i * self.enemyDataSize
            enemies.append(ff7.decodeKernelText(self.data[offset:offset + self.maxStringSize], japanese))

        return enemies

    # Return the ability names defined in the scene.
    def getAbilityNames(self, japanese = False):
        abilities = []

        for i in range(32):
            offset = self.abilitiesOffset + i * self.maxStringSize
            abilities.append(ff7.decodeKernelText(self.data[offset:offset + self.maxStringSize], japanese))

        return abilities

    # Set the enemy names.
    def setEnemyNames(self, enemies, japanese = False):
        for i in range(3):
            rawString = ff7.encodeKernelText(enemies[i], japanese)
            rawStringSize = len(rawString)

            if rawStringSize > self.maxStringSize:
                raise EnvironmentError("Enemy name '%s' in scene %d is too long when encoded (%d > %d bytes)" % (enemies[i], self.index, rawStringSize, self.maxStringSize))

            if rawStringSize < self.maxStringSize:
                rawString += bytes([0xff] * (self.maxStringSize - rawStringSize))  # pad with 0xff bytes

            offset = self.enemyDataOffset + i * self.enemyDataSize
            self.data = self.data[:offset] + rawString + self.data[offset + self.maxStringSize:]

    # Set the ability names.
    def setAbilityNames(self, abilities, japanese = False):
        for i in range(32):
            rawString = ff7.encodeKernelText(abilities[i], japanese)
            rawStringSize = len(rawString)

            if rawStringSize > self.maxStringSize:
                raise EnvironmentError("Ability name '%s' in scene %d is too long when encoded (%d > %d bytes)" % (abilities[i], self.index, rawStringSize, self.maxStringSize))

            if rawStringSize < self.maxStringSize:
                rawString += bytes([0xff] * (self.maxStringSize - rawStringSize))  # pad with 0xff bytes

            offset = self.abilitiesOffset + i * self.maxStringSize
            self.data = self.data[:offset] + rawString + self.data[offset + self.maxStringSize:]

    # Return the list of message strings in the scene scripts.
    def getStrings(self, japanese = False):
        strings = []

        for scriptsOfEnemy in self.enemyScripts:
            if scriptsOfEnemy is None:
                continue

            for script in scriptsOfEnemy:
                if script is None:
                    continue

                for instr in script:
                    if instr.op == Op.MES:
                        rawString = instr.code[1:]
                        strings.append(ff7.decodeKernelText(rawString, japanese))

        return strings

    # Replace the message strings in the scene scripts.
    def setStrings(self, strings, japanese = False):
        currentString = 0

        for scriptsOfEntity in self.enemyScripts:
            if scriptsOfEntity is None:
                continue

            for script in scriptsOfEntity:
                if script is None:
                    continue

                # Changing strings of MES instructions changes their size,
                # so we need to fixup jump targets. We do this by first
                # converting target offsets to target instruction indexes,
                # changing instructions, and then converting the indexes
                # back to offsets again.

                # Construct list of all instruction offsets
                instrOffsets = [instr.offset for instr in script]

                # Find the target instruction indexes of all jumps
                jumpMap = {}  # maps index of jump instruction to index of target

                for index in range(len(script)):
                    instr = script[index]

                    if instr.op in [Op.JMPZ, Op.JMPNE, Op.JMP]:
                        targetOffset = struct.unpack("<H", instr.code[1:])[0]
                        targetIndex = instrOffsets.index(targetOffset)
                        jumpMap[index] = targetIndex

                # Replace the strings in all MES instructions
                for index in range(len(script)):
                    if script[index].op == Op.MES:
                        rawString = ff7.encodeKernelText(strings[currentString], japanese)
                        script[index].setArg(rawString)
                        currentString += 1

                # Recalculate all instruction offsets
                offset = 0
                for index in range(len(script)):
                    script[index].setOffset(offset)
                    offset += script[index].size

                # Fixup the target offsets of jumps
                for index in range(len(script)):
                    if script[index].op in [Op.JMPZ, Op.JMPNE, Op.JMP]:
                        targetIndex = jumpMap[index]
                        targetOffset = script[targetIndex].offset
                        script[index].setArg(struct.pack("<H", targetOffset))

        # Convert scripts back to binary data
        self.insertScripts(self.enemyScripts, self.aiDataOffset, 3, len(self.data))


# Battle scene archive file (SCENE.BIN)
class Archive:
    blockSize = 0x2000
    pointerTableSize = 0x40
    maxSceneSize = 0x1e80  # maximum size of uncompressed scene

    # Parse the scene archive from an open file object.
    def __init__(self, fileobj):

        self.sceneData = []
        self.sceneIndexTable = []  # index of first scene in each block

        sceneIndex = 0

        # Read all blocks
        while True:

            # Read the next block
            block = fileobj.read(self.blockSize)
            if len(block) < self.blockSize:
                break

            # Parse the pointer table
            pointers = struct.unpack_from("<16L", block)

            offsets = []
            for p in pointers:
                if p == 0xffffffff:
                    break

                offsets.append(p << 2)

            numScenes = len(offsets)
            offsets.append(self.blockSize)  # dummy offset to determine end of last scene

            self.sceneIndexTable.append(sceneIndex)

            # Extract all scenes in the block
            for i in range(numScenes):
                start = offsets[i]
                end = offsets[i + 1]
                assert end >= start

                buffer = io.BytesIO(block[start:end].rstrip(b'\xff'))
                zipper = gzip.GzipFile(fileobj = buffer, mode = "rb")
                scene = zipper.read(self.maxSceneSize)

                self.sceneData.append(scene)
                sceneIndex += 1

    # Return the number of scenes (should be 256).
    def numScenes(self):
        return len(self.sceneData)

    # Return the scene with the given index.
    def getScene(self, index):
        return Scene(self.sceneData[index], index)

    # Replace the scene with the given index.
    def setScene(self, index, scene):
        self.sceneData[index] = scene.getData()

    # Write the archive to a file object, truncating the file.
    def writeToFile(self, fileobj):

        # Truncate file
        fileobj.seek(0)
        fileobj.truncate()

        # Scene index table will be rebuilt
        self.sceneIndexTable = []

        sceneIndex = 0
        numScenes = len(self.sceneData)

        # Process all scenes
        block = bytearray()
        pointers = []
        firstIndexInBlock = 0

        while True:
            writeBlock = False

            if sceneIndex >= numScenes:

                # All scenes done, write the last block
                cmpData = None
                writeBlock = True

            else:

                # Compress next scene
                cmpData = ff7.compressGzip(self.sceneData[sceneIndex])
                if len(cmpData) % 4 != 0:
                    cmpData += bytes([0xff] * (4 - len(cmpData) % 4))  # pad scene to 4-byte boundary

                if self.pointerTableSize + len(block) + len(cmpData) > self.blockSize:

                    # Scene doesn't fit in current block, write it first
                    writeBlock = True

            if writeBlock:

                # Write current block to file
                for p in pointers:
                    fileobj.write(struct.pack("<L", p >> 2))
                for i in range(16 - len(pointers)):
                    fileobj.write(struct.pack("<L", 0xffffffff))

                if len(block) < self.blockSize - self.pointerTableSize:
                    block.extend(bytes([0xff] * (self.blockSize - self.pointerTableSize - len(block))))  # pad with 0xff bytes

                fileobj.write(block)

                self.sceneIndexTable.append(firstIndexInBlock)

                block = bytearray()
                pointers = []
                firstIndexInBlock = sceneIndex

            if sceneIndex >= numScenes:

                # All done
                break

            else:

                # Add compressed scene to block
                pointers.append(len(block) + self.pointerTableSize)
                block.extend(cmpData)

                sceneIndex += 1
