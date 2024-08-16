#
# wa.archive - Wild Arms archive handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct


# Archive file holding 1..63 sections referenced by a 64-entry pointer table
# at the start. A null pointer terminates the table.
class Archive:

    numPointers = 64

    # Parse the archive from an open file object.
    def __init__(self, fileobj):
        self.sections = []

        # Read the pointer table
        data = fileobj.read(self.numPointers * 4)
        pointers = struct.unpack("<%dL" % self.numPointers, data)

        self.basePointer = pointers[0]

        # Compute the section sizes from the pointers and read the section data
        for i in xrange(len(pointers) - 1):
            if pointers[i]:
                if pointers[i + 1]:
                    self.sections.append(fileobj.read(pointers[i + 1] - pointers[i]))
                else:
                    # Last section, read rest of file
                    self.sections.append(fileobj.read())
                    break

    # Return the number of sections in the archive.
    def numSections(self):
        return len(self.sections)

    # Return the list of all sections in the archive.
    def getSections(self):
        return self.sections

    # Retrieve the data of a section as a byte string.
    def getSection(self, index):
        return self.sections[index]

    # Set the data of a section.
    def setSection(self, index, data):
        self.sections[index] = data

        # Pad section data to a 32-bit boundary
        l = len(data)
        if l % 4:
            self.sections[index] += '\0' * (4 - (l % 4))

    # Write all sections to a file object, truncating the file.
    def writeToFile(self, fileobj):
        fileobj.seek(0)
        fileobj.truncate()

        # Write the pointer table
        p = self.basePointer
        for index in xrange(self.numPointers):
            if index < len(self.sections):
                fileobj.write(struct.pack("<L", p))
                p += len(self.sections[index])
            else:
                fileobj.write(struct.pack("<L", 0))

        # Write the section data
        for section in self.sections:
            fileobj.write(section)

        # Pad file to CD sector boundary
        offset = fileobj.tell() % 2048
        if offset:
            fileobj.write('\0' * (2048 - offset))
