#
# wa.lzss - LZSS decompression algorithm
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct


# Wild Arms uses references with 12-bit offsets and 4-bit lengths,
# corresponding to a 4096-byte window, and reference lengths in the range
# 3..18 bytes.
WSIZE = 0x1000    # window size
WMASK = 0x0fff    # window offset bit mask

MAX_REF_LEN = 18  # maximum reference length
MIN_REF_LEN = 3   # minimum reference length


# Decompress LZSS-compressed data, prefixed by a 32-bit uncompressed length
# field.
def decompress(data):
    if isinstance(data, str):
        data = bytearray(data)

    # Input size and input offset
    dataSize = len(data)
    i = 0

    # Dictionary and dictionary offset
    dictionary = bytearray(WSIZE)
    j = WSIZE - MAX_REF_LEN

    # Output data, output size, and output offset
    output = bytearray()
    outputSize = struct.unpack_from("<L", data, i)[0]
    k = 0
    i += 4

    while k < outputSize and i < dataSize:

        # Read next flags byte
        flags = data[i]
        i += 1

        # Process 8 literals or references
        for bit in range(8):
            if k >= outputSize:
                break

            if flags & (1 << bit):

                # Copy literal value
                c = data[i]
                i += 1

                output.append(c)
                k += 1

                # Store in dictionary
                dictionary[j] = c
                j = (j + 1) & WMASK

            else:

                # Resolve dictionary reference
                # (strange encoding: lower 8 bits of offset in first byte,
                # upper 4 bits of offset in upper 4 bits of second byte)
                offset = data[i] | ((data[i+1] & 0xf0) << 4)
                length = (data[i+1] & 0x0f) + MIN_REF_LEN
                i += 2

                while length > 0:

                    # Copy dictionary value
                    c = dictionary[offset]
                    offset = (offset + 1) & WMASK

                    output.append(c)
                    k += 1

                    # Store in dictionary
                    dictionary[j] = c
                    j = (j + 1) & WMASK

                    length -= 1

    return output


# Find the size of a block of LZSS-compressed data.
def compressedSize(data):
    if isinstance(data, str):
        data = bytearray(data)

    # Perform a dry run of the LZSS decompression to find the end of the
    # compressed data.
    maxSize = struct.unpack_from("<L", data)[0]
    i = 4
    k = 0

    while k < maxSize:

        # Read next flags byte
        flags = data[i]
        i += 1

        # Process 8 literals or references
        for bit in range(8):
            if k >= maxSize:
                break

            if flags & (1 << bit):

                # Literal byte
                i += 1
                k += 1

            else:

                # Two-byte dictionary reference
                k += (data[i+1] & 0x0f) + MIN_REF_LEN
                i += 2

    return i


# Dictionary for LZSS compression
class Dictionary:

    # Initialize the dictionary.
    def __init__(self):

        # For each reference length there is one dictionary mapping substrings
        # to dictionary offsets.
        self.d = [{} for i in range(0, MAX_REF_LEN + 1)]
        self.ptr = 0

        # For each reference length there is also a reverse dictionary
        # mapping dictionary offsets to substrings. This makes removing
        # dictionary entries more efficient.
        self.r = [{} for i in range(0, MAX_REF_LEN + 1)]

    # Add all initial substrings of a string to the dictionary.
    def add(self, s):
        s = bytes(s)

        maxLength = MAX_REF_LEN
        if maxLength > len(s):
            maxLength = len(s)

        offset = self.ptr

        # Generate all substrings
        for length in range(MIN_REF_LEN, maxLength + 1):
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
        s = bytes(s)

        maxLength = MAX_REF_LEN
        if maxLength > len(s):
            maxLength = len(s)

        for length in range(maxLength, MIN_REF_LEN - 1, -1):
            substr = s[:length]

            try:
                offset = self.d[length][substr]
                return (offset, length)
            except KeyError:
                pass

        raise KeyError


# Compress an 8-bit string to LZSS format and prefix it with a 32-bit
# uncompressed length field.
def compress(data):
    dictionary = Dictionary()

    # Prime the dictionary
    dictionary.ptr = WSIZE - 2*MAX_REF_LEN
    for i in range(MAX_REF_LEN):
        dictionary.add(b'\0' * (MAX_REF_LEN - i) + data[:i])

    # Output data starts with uncompressed data length
    dataSize = len(data)
    output = bytearray(struct.pack("<L", dataSize))

    i = 0
    while i < dataSize:

        # Accumulated output chunk
        accum = bytearray()

        # Process 8 literals or references at a time
        flags = 0
        for bit in range(8):
            if i >= dataSize:
                break

            # Next substring in dictionary?
            try:
                substr = data[i:i + MAX_REF_LEN]
                offset, length = dictionary.find(substr)

                # Yes, append dictionary reference
                accum.append(offset & 0xff)
                accum.append(((offset >> 4) & 0xf0) | (length - MIN_REF_LEN))

                # Update dictionary
                for j in range(length):
                    dictionary.add(data[i + j:i + j + MAX_REF_LEN])

                i += length

            except KeyError:

                # Append literal value
                v = data[i]
                accum.append(v)

                flags |= (1 << bit)

                # Update dictionary
                dictionary.add(data[i:i + MAX_REF_LEN])

                i += 1

        # Chunk complete, add to output
        output.append(flags)
        output.extend(accum)

    return output
