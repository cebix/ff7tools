#
# ff7.binlz - Final Fantasy VII LZSS archive handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import os
import struct

import ff7


# LZSS archive file, stores LZSS compressed data
class ArchiveFile:

    def __init__(self, index, cmpData = b""):
        self.index = index
        self.cmpData = cmpData

    # Return the decompressed file data as an 8-bit string.
    def getData(self):
        cmpSize = struct.unpack_from("<L", self.cmpData)[0]
        return ff7.decompressLzss(self.cmpData[4:4 + cmpSize])

    # Replace the file data and compress it.
    def setData(self, data):
        cmpData = ff7.compressLzss(data)
        self.cmpData = struct.pack("<L", len(cmpData)) + cmpData

        while len(self.cmpData) % 4:
            self.cmpData += bytes([0])  # align to 32-bit


# LZSS archive (sequence of possibly LZSS compressed files with an offset
# table at the start)
class Archive:

    # Parse the archive data from an open file object.
    def __init__(self, fileobj):
        self.fileList = []

        # Read the offset table
        firstOffset = struct.unpack("<L", fileobj.read(4))[0]
        assert firstOffset % 4 == 0

        numFiles = firstOffset // 4

        offsets = [firstOffset]
        for fileNum in range(numFiles - 1):
            offsets.append(struct.unpack("<L", fileobj.read(4))[0])

        pos = fileobj.tell()
        fileobj.seek(0, os.SEEK_END)
        offsets.append(fileobj.tell())  # dummy offset to determine size of last file
        fileobj.seek(pos)

        # Extract all files
        for fileNum in range(numFiles):
            cmpDataSize = offsets[fileNum + 1] - offsets[fileNum]
            self.fileList.append(ArchiveFile(fileNum, fileobj.read(cmpDataSize)))

    # Return the number of files in the archive.
    def numFiles(self):
        return len(self.fileList)

    # Return the file with the given index.
    # Raises IndexError if there is no such file.
    def getFile(self, index):
        return self.fileList[index]

    # Return the list of all files in the archive.
    def getFiles(self):
        return self.fileList

    # Add a file, possibly replacing a file with the same index.
    def addFile(self, f):
        while len(self.fileList) < f.index:
            self.fileList.append(ArchiveFile(len(self.fileList)))

        self.fileList[f.index] = f

    # Write the archive to a file object, truncating the file.
    def writeToFile(self, fileobj):
        fileobj.seek(0)
        fileobj.truncate()

        # Write the offset table
        offset = self.numFiles() * 4
        for f in self.fileList:
            fileobj.write(struct.pack("<L", offset))
            offset += len(f.cmpData)

        # Write the file data
        for f in self.fileList:
            fileobj.write(f.cmpData)
