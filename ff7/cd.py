#
# ff7.cd - Final Fantasy VII disc image handling
#
# Copyright (C) 2014 Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#


import os
import struct


# Disc image object, handles 2048-byte-per-sector ISO images as well as
# 2352-byte-per-sector "raw" mode 2 images.
class Image:

    # Open the specified image file and check for a valid ISO9660 file system.
    def __init__(self, imageFileName):
        self.blockSize = None      # Number of bytes in one block (for seeking)
        self.blockOffset = None    # Offset of user data of first sector
        self.rootDirSector = None  # Root directory start sector
        self.rootDirSize = None    # Size of root directory extent

        # Open the file
        self.file = open(imageFileName, "rb")

        # Determine the image type
        header = self.file.read(12)

        self.file.seek(0, os.SEEK_END)
        fileSize = self.file.tell()

        if header == "\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00" and fileSize % 2352 == 0:

            # Sync header present, assume a raw image
            self.blockSize = 2352
            self.blockOffset = 0x18

        elif fileSize % 2048 == 0:

            # Assume a normal ISO image
            self.blockSize = 2048
            self.blockOffset = 0

        else:
            raise EnvironmentError, "'%s' does not appear to be a disc image file (invalid file size)" % imageFileName

        # Read and check the PVD
        pvd = self.readExtent(16, 2048)

        if pvd[:7] != "\x01CD001\x01":
            raise EnvironmentError, "'%s' is not a disc image file (volume descriptor not found)" % imageFileName

        # Find the root directory
        self.rootDirSector, self.rootDirSize = struct.unpack_from("<L4xL", pvd, 0x9e)

    # Close the image file.
    def close(self):
        self.file.close()

    # Read contiguous data from the image given the start sector and number
    # of bytes to read. Returns the data as a byte string.
    def readExtent(self, firstSector, numBytes):
        data = ""
        sector = firstSector

        while numBytes > 0:
            self.file.seek(sector * self.blockSize + self.blockOffset)
            sectorData = self.file.read(2048)

            if len(sectorData) < 2048:
                raise ValueError, "Error reading sector %d of disc image" % sector

            sector += 1

            if numBytes > 2048:
                data += sectorData
                numBytes -= 2048
            else:
                data += sectorData[:numBytes]
                numBytes = 0

        return data

    # Find a file or directory in the image by path name, returning a
    # (firstSector, numBytes) tuple. Raises a KeyError if the file or
    # directory was not found.
    def findExtent(self, pathName):

        # Split the path into components
        path = pathName.lstrip('/').split('/')

        # Start the search at the root directory
        dirSector = self.rootDirSector
        dirSize = self.rootDirSize

        # Search iteratively along the path
        while len(path) > 0:

            # Read the directory
            dir = self.readExtent(dirSector, dirSize)

            # Search directory records for the next component in the path
            firstSector = None
            numBytes = None

            offset = 0
            while (firstSector is None) and (offset < dirSize):

                # Get record length and type
                recLen = ord(dir[offset])
                if recLen == 0:
                    offset += 1  # empty padding at end of sector
                    continue

                recType = ord(dir[offset + 0x19])

                # Compare entry name
                nameLen = ord(dir[offset + 0x20])
                name = dir[offset + 0x21:offset + 0x21 + nameLen]
                name = name.split(';')[0]  # strip file version numbers

                if name == path[0]:

                    # Found it
                    firstSector, numBytes = struct.unpack_from("<L4xL", dir, offset + 2)

                    if (len(path) > 1) and (recType & 0x02) == 0:

                        # Expected a directory but found a file
                        raise KeyError, "'%s' not found in disc image" % pathName

                # Move to next record
                offset += recLen

            if firstSector is None:
                raise KeyError, "'%s' not found in disc image" % pathName

            if len(path) == 1:

                # Found the file or directory
                return (firstSector, numBytes)

            else:

                # Descend to subdirectory and continue
                dirSector = firstSector
                dirSize = numBytes
                path.pop(0)

    # Read a file from the image specified by path name, returning the file
    # data as a byte string. Raises a KeyError if the file was not found.
    def readFile(self, pathName):
        firstSector, numBytes = self.findExtent(pathName)
        return self.readExtent(firstSector, numBytes)
