#
# wa - Utility package for working with Wild Arms game data
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

__author__ = "Christian Bauer <www.cebix.net>"
__version__ = "1.1"


import os
import re
import struct
import io

from . import cd
from . import data
from . import text
from . import map
from . import archive
from . import lzss
from .version import Version


# Object representing a CD image of the game.
class GameImage(cd.Image):
    def __init__(self, imagePath):
        cd.Image.__init__(self, imagePath)

    # Retrieve a file from the image, returning an open file object.
    def openFile(self, subDir, fileName):
        data = self.readFile(subDir + '/' + fileName)
        f = io.BytesIO(data)
        return f

    # Check for the existence of a file in the image.
    def hasFile(self, subDir, fileName):
        try:
            self.findExtent(subDir + '/' + fileName)
            return True
        except:
            return False


# Object representing a directory of the game's files.
class GameDirectory:
    def __init__(self, dirPath):
        self.basePath = dirPath

    # Retrieve a file from the directory, returning an open file object.
    def openFile(self, subDir, fileName):
        filePath = os.path.join(self.basePath, subDir, fileName)
        return open(filePath, "rb")

    # Check for the existence of a file in the directory.
    def hasFile(self, subDir, fileName):
        filePath = os.path.join(self.basePath, subDir, fileName)
        return os.path.isfile(filePath)


# Check the game version, returns the tuple (version, execFileName).
# The 'image' can be a GameImage or a GameDirectory.
def checkVersion(image):

    # Find the name of the executable
    f = image.openFile("", "SYSTEM.CNF")
    line = f.readline()

    m = re.match(br"BOOT *= *cdrom:\\EXE\\([\w.]+)(;1)?", line)
    if not m:
        raise EnvironmentError("Unrecognized line '%s' in SYSTEM.CNF (not a Wild Arms image?)" % line)

    execFileName = m.group(1).decode("ascii")

    if execFileName == "SCPS_100.28":
        f = image.openFile("EXE", "WILDARMS.EXE")
        data = f.read(32)
        if data[16] == 0x10:
            version = Version.JP2
        else:
            version = Version.JP1
    elif execFileName == "SCUS_946.08":
        version = Version.US
    elif execFileName == "SCES_003.21":
        version = Version.EN
    elif execFileName == "SCES_011.71":
        version = Version.FR
    elif execFileName == "SCES_011.72":
        version = Version.DE
    elif execFileName == "SCES_011.73":
        version = Version.IT
    elif execFileName == "SCES_011.74":
        version = Version.ES
    else:
        raise EnvironmentError("Unrecognized game version")

    return (version, execFileName)


# Create and return a GameImage or GameDirectory object given the path
# name of a CD image or a directory.
def openImage(path):
    if os.path.isfile(path):
        image = GameImage(path)
    elif os.path.isdir(path):
        image = GameDirectory(path)
    else:
        raise EnvironmentError("'%s' is not a directory or disc image file" % path)

    image.version, image.execFileName = checkVersion(image)
    return image
