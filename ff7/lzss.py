#
# ff7.lzss - LZSS compression and decompression algorithms
#
# Copyright (C) 2014 Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#


# Final Fantasy VII uses references with 12-bit offsets and 4-bit lengths,
# corresponding to a 4096-byte window, and reference lengths in the range
# 3..18 bytes.
WSIZE = 0x1000    # window size
WMASK = 0x0fff    # window offset bit mask

MAX_REF_LEN = 18  # maximum reference length
MIN_REF_LEN = 3   # minimum reference length


# Decompress an 8-bit string from LZSS format.
def decompress(data):

    # Input offset and input size
    i = 0
    dataSize = len(data)

    # Output offset and output data
    j = 0
    output = ""

    while i < dataSize:

        # Read next flags byte
        flags = ord(data[i])
        i += 1

        # Process 8 literals or references
        for bit in xrange(8):
            if i >= dataSize:
                break

            if flags & (1 << bit):

                # Copy literal value
                output += data[i]
                i += 1
                j += 1

            else:

                # Resolve dictionary reference
                # (strange encoding: lower 8 bits of offset in first byte,
                # upper 4 bits of offset in upper 4 bits of second byte)
                offset = ord(data[i]) | ((ord(data[i+1]) & 0xf0) << 4)
                length = (ord(data[i+1]) & 0x0f) + MIN_REF_LEN
                i += 2

                ref = j - ((j + 0xfee - offset) & 0xfff)
                while length > 0:
                    if ref < 0:  # references before start of output resolve to 0 bytes
                        output += '\0'
                    else:
                        output += output[ref]

                    j += 1
                    ref += 1
                    length -= 1

    return output


# Dictionary for LZSS compression
class Dictionary:

    # Initialize the dictionary.
    def __init__(self):

        # For each reference length there is one dictionary mapping substrings
        # to dictionary offsets.
        self.d = [{} for i in xrange(0, MAX_REF_LEN + 1)]
        self.ptr = 0

        # For each reference length there is also a reverse dictionary
        # mapping dictionary offsets to substrings. This makes removing
        # dictionary entries more efficient.
        self.r = [{} for i in xrange(0, MAX_REF_LEN + 1)]

    # Add all initial substrings of a string to the dictionary.
    def add(self, s):
        maxLength = MAX_REF_LEN
        if maxLength > len(s):
            maxLength = len(s)

        offset = self.ptr

        # Generate all substrings
        for length in xrange(MIN_REF_LEN, maxLength + 1):
            substr = s[:length]

            # Remove obsolete mapping, if present
            try:
                prevOffset = self.d[length][substr]
                del self.r[length][prevOffset]
            except KeyError:
                pass

            try:
                prevSubstr = self.r[length][offset]
                del self.d[length][prevSubstr]
            except KeyError:
                pass

            # Add new mapping
            self.d[length][substr] = offset
            self.r[length][offset] = substr

        # Advance dictionary pointer
        self.ptr = (self.ptr + 1) & WMASK

    # Find any of the initial substrings of a string in the dictionary,
    # looking for long matches first. Returns an (offset, length) tuple if
    # found. Raises KeyError if not found.
    def find(self, s):
        maxLength = MAX_REF_LEN
        if maxLength > len(s):
            maxLength = len(s)

        for length in xrange(maxLength, MIN_REF_LEN - 1, -1):
            substr = s[:length]

            try:
                offset = self.d[length][substr]
                if offset != self.ptr:  # the FF7 LZSS decompressor can't handle this case
                    return (offset, length)
            except KeyError:
                pass

        raise KeyError


# Compress an 8-bit string to LZSS format.
def compress(data):
    dictionary = Dictionary()

    # Prime the dictionary
    dictionary.ptr = WSIZE - 2*MAX_REF_LEN
    for i in xrange(MAX_REF_LEN):
        dictionary.add('\0' * (MAX_REF_LEN - i) + data[:i])

    # Output data
    output = ""

    i = 0
    dataSize = len(data)

    while i < dataSize:

        # Accumulated output chunk
        accum = ""

        # Process 8 literals or references at a time
        flags = 0
        for bit in xrange(8):
            if i >= dataSize:
                break

            # Next substring in dictionary?
            try:
                substr = data[i:i + MAX_REF_LEN]
                offset, length = dictionary.find(substr)

                # Yes, append dictionary reference
                accum += chr(offset & 0xff) + chr(((offset >> 4) & 0xf0) | (length - MIN_REF_LEN))

                # Update dictionary
                for j in xrange(length):
                    dictionary.add(data[i + j:i + j + MAX_REF_LEN])

                i += length

            except KeyError:

                # Append literal value
                v = data[i]
                accum += v

                flags |= (1 << bit)

                # Update dictionary
                dictionary.add(data[i:i + MAX_REF_LEN])

                i += 1

        # Chunk complete, add to output
        output += chr(flags)
        output += accum

    return output
