#
# ff7.kernel - Final Fantasy VII kernel data handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct

import ff7
from . import ff7text


# Kernel archive file, stores data in GZIP format
class ArchiveFile:

    def __init__(self, dirID, index, cmpData = b"", rawDataSize = 0):
        self.dirID = dirID
        self.index = index
        self.cmpData = cmpData
        self.rawDataSize = rawDataSize

    # Return the decompressed file data as an 8-bit string.
    def getData(self):
        return ff7.decompressGzip(self.cmpData)

    # Replace the file data and compress it.
    def setData(self, data):
        self.rawDataSize = len(data)
        self.cmpData = ff7.compressGzip(data)


# Kernel archive (sequence of gzipped files prefixed with 16-bit size
# information and directory ID)
class Archive:

    # Parse the archive data from an open file object.
    def __init__(self, fileobj):
        self.name = fileobj.name
        self.fileList = []

        # Extract all files
        index = 0
        prevDirID = None

        while True:

            # Parse the file header
            header = fileobj.read(6)
            if len(header) < 6:
                break

            cmpDataSize, rawDataSize, dirID = struct.unpack("<HHH", header)

            # The index starts from 0 when the directory ID changes
            if dirID != prevDirID:
                index = 0
                prevDirID = dirID

            # Read the file data and append it to the list
            cmpData = fileobj.read(cmpDataSize)
            self.fileList.append(ArchiveFile(dirID, index, cmpData, rawDataSize))

            index += 1

    # Return the file with the given directory ID and index.
    # Raises IndexError if there is no such file.
    def getFile(self, dirID, index):
        for f in self.fileList:
            if f.dirID == dirID and f.index == index:
                return f

        raise IndexError("No file with directory ID %d, index %d in archive '%s'" % (dirID, index, self.name))

    # Return the list of all files in the archive.
    def getFiles(self):
        return self.fileList

    # Return the list of files with a given directory ID (may be empty).
    def directory(self, dirID):
        return [f for f in self.fileList if f.dirID == dirID]

    # Add a file, possibly replacing a file with the same directory ID and index.
    def addFile(self, f):
        for i in range(len(self.fileList)):
            if self.fileList[i].dirID == f.dirID and self.fileList[i].index == f.index:
                self.fileList[i] = f
                return

        self.fileList.append(f)

    # Write the archive to a file object, truncating the file.
    def writeToFile(self, fileobj):
        fileobj.seek(0)
        fileobj.truncate()

        # Write all files
        for f in self.fileList:

            # Write the header
            header = struct.pack("<HHH", len(f.cmpData), f.rawDataSize, f.dirID)
            fileobj.write(header)

            # Write the file data
            fileobj.write(f.cmpData)


# Kernel string list, as typically found inside a kernel archive (header of
# 16-bit offsets followed by compressed string data)
class StringList:

    # Make a string list object from raw data.
    # In theory, the number of strings could be inferred from the header
    # offsets, but to avoid unpleasant surprises we require the caller to
    # supply it.
    def __init__(self, data = None, numStrings = 0, japanese = False):
        self.stringList = []
        self.japanese = japanese

        # Parse the offset table
        offsets = []
        for i in range(numStrings):
            offsets.append(struct.unpack_from("<H", data, i*2)[0])

        # Extract the strings
        for offset in offsets:
            rawString, endOfString = self._extract(data, offset, len(data))
            assert endOfString
            self.stringList.append(ff7text.decodeKernel(rawString, japanese))

    # Extract a single string from the raw data. Returns a tuple consisting
    # of the extracted string and a flag which indicates that the end of the
    # string has been reached.
    def _extract(self, data, startOffset, endOffset):
        s = b""
        endOfString = False

        i = startOffset
        while i < endOffset:
            c = data[i]
            i += 1

            if c == 0xf9:

                # Reference to previous input data (poor man's dictionary compression...)
                c = data[i]
                i += 1

                refLength = (c >> 6)*2 + 4
                refOffset = i - (c & 0x3f) - 3

                refData, refHasEnd = self._extract(data, refOffset, refOffset + refLength)
                s += refData

                if refHasEnd:

                    # End of string reached in reference, stop extracting
                    endOfString = True
                    break

            elif c >= 0xea and c <= 0xf0:

                # Kernel variable code, copy two argument bytes verbatim
                if i >= endOffset - 1:
                    raise IndexError("Premature end of kernel string in variable reference")

                s += bytes([c])
                s += data[i:i+2]
                i += 2

            else:

                # Regular character, append it
                s += bytes([c])

                if c == 0xff:

                    # End of string reached, stop extracting
                    endOfString = True
                    break

        return (s, endOfString)

    # Return the list of all strings as unicode objects.
    def getStrings(self):
        return self.stringList

    # Return one string as a unicode object.
    def getString(self, index):
        return self.stringList[index]

    # Replace the entire string list.
    def setStrings(self, stringList):
        self.stringList = stringList

    # Replace one string.
    def setString(self, index, string):
        self.stringList[index] = string

    # Encode string list to binary data and return it.
    def getData(self, compress = False):
        numStrings = len(self.stringList)

        # Encode all strings
        offsets = []
        data = bytearray()

        for string in self.stringList:
            rawString = ff7text.encode(string, False, self.japanese)

            # Already in string data?
            offset = data.find(rawString)
            if offset >= 0:

                # Yes, just push the offset
                offsets.append(offset)

            else:

                # No, append a new string
                offset = len(data)
                offsets.append(offset)

                # Scan for usable references to previous string data
                i = 0
                while i < len(rawString):
                    c = rawString[i]

                    if c >= 0xea and c <= 0xf0:

                        # Kernel variable code, copy verbatim
                        data.extend(rawString[i:i+3])
                        i += 3

                    elif c == 0xf8:

                        # Text box color code, copy verbatim
                        data.extend(rawString[i:i+2])
                        i += 2

                    elif compress:

                        # Look for 10/8/6/4-byte substring in last 64 bytes of data
                        found = False
                        for refLength in range(10, 2, -2):
                            searchFor = rawString[i:i + refLength]
                            if len(searchFor) < refLength:
                                continue

                            # Don't search for control codes; the game cannot resolve them
                            if any((x >= 0xe0 and x <= 0xfe) for x in searchFor):
                                continue

                            searchStart = len(data) - 64
                            if searchStart < 0:
                                searchStart = 0

                            refOffset = data.find(searchFor, searchStart)
                            if refOffset >= 0:

                                # Found, encode reference
                                data.append(0xf9)
                                data.append(((refLength - 4) << 5) | (len(data) - refOffset - 2))

                                i += refLength

                                found = True
                                break

                        if not found:

                            # Encode literal value
                            data.append(c)
                            i += 1

                    else:

                        # Regular character
                        data.append(c)
                        i += 1

        if len(data) % 2:
            data.append(0xff)  # align to 16-bit boundary

        # Encode the offset table
        offsetData = bytearray()
        for offset in offsets:
            offsetData.extend(struct.pack("<H", offset + numStrings*2))

        return offsetData + data
