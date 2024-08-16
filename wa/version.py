#
# wa.version - Wild Arms game versions
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#


def _enum(**enums):
    return type('Enum', (), enums)

# Supported game versions
Version = _enum(
    JP1 = 1,  # Japanese original release (SCPS-10028)
    JP2 = 2,  # Japanese re-release (SCPS-10028)
    US  = 3,  # US release (SCUS-94608)
    EN  = 4,  # English European release (SCES-00321)
    FR  = 5,  # French European release (SCES-01171)
    DE  = 6,  # German European release (SCES-01172)
    IT  = 7,  # Italian European release (SCES-01173)
    ES  = 8,  # Spanish European release (SCES-01174)
)

def isJapanese(version):
    return version in [Version.JP1, Version.JP2]
