#
# ff7 - Utility package for working with Final Fantasy VII data
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

__author__ = "Christian Bauer <www.cebix.net>"
__version__ = "1.4"


import os
import re
import gzip
import zlib
import struct
import io

from . import lzss
from . import binlz
from . import ff7text
from . import kernel
from . import field
from . import tutorial
from . import scene
from . import world
from . import data
from . import cd


def _enum(**enums):
    return type('Enum', (), enums)


# Supported game versions
Version = _enum(
    EN = 1,  # English European release (SCES-00867)
    FR = 2,  # French European release (SCES-00868)
    DE = 3,  # German European release (SCES-00869)
    ES = 4,  # Spanish European release (SCES-00900)
    US = 5,  # US release (SCUS-94163)
    JP = 6,  # Japanese International release (SLPS-01057)
    JO = 7,  # Original Japanese release (SLPS-00700)
)

def isEuropean(version):
    return version in [Version.EN, Version.FR, Version.DE, Version.ES]

def isJapanese(version):
    return version in [Version.JP, Version.JO]


# Retrieve a file from a disc image.
def _retrieveFileFromImage(image, subDir, fileName):
    filePath = subDir + '/' + fileName

    data = image.readFile(filePath)

    f = io.BytesIO(data)
    f.name = filePath  # kernel.Archive needs this
    return f


# Retrieve a file from a disc directory.
def _retrieveFileFromDir(discPath, subDir, fileName):
    filePath = os.path.join(discPath, subDir, fileName)
    return open(filePath, "rb")


# Retrieve a file from the disc directory or image.
def retrieveFile(discPath, subDir, fileName):
    if isinstance(discPath, cd.Image):
        return _retrieveFileFromImage(discPath, subDir, fileName)
    else:
        return _retrieveFileFromDir(discPath, subDir, fileName)


# Check whether a file exists in a disc image.
def _fileExistsInImage(image, subDir, fileName):
    try:
        image.findExtent(subDir + '/' + fileName)
        return True
    except:
        return False


# Check whether a file exists in a disc directory.
def _fileExistsInDir(discPath, subDir, fileName):
    filePath = os.path.join(discPath, subDir, fileName)
    return os.path.isfile(filePath)


# Check whether a file exists in the disc directory or image.
def fileExists(discPath, subDir, fileName):
    if isinstance(discPath, cd.Image):
        return _fileExistsInImage(discPath, subDir, fileName)
    else:
        return _fileExistsInDir(discPath, subDir, fileName)


# Check the game version, returns the tuple (version, discNumber, execFileName).
# The 'discPath' can be either a directory name, or a cd.Image object.
def checkDisc(discPath):

    # Retrieve the DISKINFO.CNF file
    f = None
    for name in ["DISKINFO.CNF", "DISKNUM.CNF"]:
        if fileExists(discPath, "MINT", name):
            f = retrieveFile(discPath, "MINT", name)
            break

    if f is None:
        raise EnvironmentError("Cannot find DISKINFO.CNF file (not a Final Fantasy VII image?)")

    discId = f.read(8)

    if discId == b"DISK0001":
        discNumber = 1
    elif discId == b"DISK0002":
        discNumber = 2
    elif discId == b"DISK0003":
        discNumber = 3
    else:
        raise EnvironmentError("Unknown disc ID '%s' in DISKINFO.CNF" % discId)

    # Find the name of the executable
    f = retrieveFile(discPath, "", "SYSTEM.CNF")
    line = f.readline()

    m = re.match(br"BOOT = cdrom:\\([\w.]+);1", line)
    if not m:
        raise EnvironmentError("Unrecognized line '%s' in SYSTEM.CNF" % line)

    execFileName = m.group(1).decode("ascii")

    if execFileName in ["SCES_008.67", "SCES_108.67", "SCES_208.67"]:
        version = Version.EN
    elif execFileName in ["SCES_008.68", "SCES_108.68", "SCES_208.68"]:
        version = Version.FR
    elif execFileName in ["SCES_008.69", "SCES_108.69", "SCES_208.69"]:
        version = Version.DE
    elif execFileName in ["SCES_009.00", "SCES_109.00", "SCES_209.00"]:
        version = Version.ES
    elif execFileName in ["SCUS_941.63", "SCUS_941.64", "SCUS_941.65"]:
        version = Version.US
    elif execFileName in ["SLPS_010.57", "SLPS_010.58", "SLPS_010.59"]:
        version = Version.JP
    elif execFileName in ["SLPS_007.00", "SLPS_007.01", "SLPS_007.02"]:
        version = Version.JO
    else:
        raise EnvironmentError("Unrecognized game version")

    return (version, discNumber, execFileName)


# Decompress an 8-bit string from GZIP format.
def decompressGzip(data):
    buffer = io.BytesIO(data)
    zipper = gzip.GzipFile(fileobj = buffer, mode = "rb")
    return zipper.read()


# Compress an 8-bit string to GZIP format.
def compressGzip(data):
    buffer = io.BytesIO()
    zipper = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, -zlib.MAX_WBITS, 6, 0)  # memlevel = 6 seems to produce smaller output

    buffer.write(b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x00")
    buffer.write(zipper.compress(data))
    buffer.write(zipper.flush())
    buffer.write(struct.pack("<L", zlib.crc32(data) & 0xffffffff))
    buffer.write(struct.pack("<L", len(data)))

    return buffer.getvalue()


# Decompress an 8-bit string from LZSS format.
def decompressLzss(data):
    return lzss.decompress(data)


# Compress an 8-bit string to LZSS format.
def compressLzss(data):
    return lzss.compress(data)


# Decode FF7 kernel text string to unicode string.
def decodeKernelText(data, japanese = False):
    return ff7text.decodeKernel(data, japanese)


# Decode FF7 field text string to unicode string.
def decodeFieldText(data, japanese = False):
    return ff7text.decodeField(data, japanese)


# Encode unicode string to FF7 kernel text string.
def encodeKernelText(text, japanese = False):
    return ff7text.encode(text, False, japanese)


# Encode unicode string to FF7 field text string.
def encodeFieldText(text, japanese = False):
    return ff7text.encode(text, True, japanese)


# Calculate the extent of a unicode string.
def textExtent(text, metrics):
    return ff7text.extent(text, metrics)
