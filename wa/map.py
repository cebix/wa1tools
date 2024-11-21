#
# wa.map - Wild Arms map and script handling
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import struct

import wa


def _enum(**enums):
    return type('Enum', (), enums)


#
# Terminology:
# - "Pointer" refers to a 32-bit value representing a PSX memory address.
#   A map data block is loaded to memory at 0x8014f000.
# - An "address" is the lower 16 bits of a pointer. This is how positions
#   within the script code are referenced by the game, for example in
#   jump instructions.
# - "Offset" refers to a byte position relative to the start of the map
#   data block.
#
# To convert from an offset to a pointer, add 0x8014f000.
# To convert from a pointer to an address, strip the upper 16 bits (& 0xffff).
#

# Start address of map in memory
mapBasePointer = 0x8014f000

# Start address of map graphics data in memory
mapGfxPointer = 0x80164000

# Convert pointer to offset.
def pointerToOffset(pointer):
    return pointer - mapBasePointer

# Convert offset to pointer.
def offsetToPointer(offset):
    return offset + mapBasePointer

# Convert offset to address.
def offsetToAddr(offset, basePointer = mapBasePointer):
    return (offset + basePointer) & 0xffff;

# Convert address to offset
def addrToOffset(addr):
    return (addr - mapBasePointer) & 0xffff;


#
# Expression opcodes
#

exOpcodes = [
    "==",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
    "&",
    "|",
    "^",
    "== 0",
    "+",
    "-",
    "*",
    "/",
    "%",
    None,
    "",
    "result",      # Result of last assignment or instruction
    "rand",        # Random value between 0 and 32767
    "var",         # Script variable
    "flag",        # Game flag (flags -1/-2 come from actor data in the map)
    "addr",        # Script address, used for referencing string literals
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    "party_size",  # Number of members in party
    "gold",        # Acquired gella
    "party",       # Party member (-1 = add member to party, -2 = remove member from party)
    "level",       # Character level
    "exp",         # Character EXP
    "status",      # Character status
    "inventory",   # Inventory item (-1 = add, -2 = remove)
    "spell",       # Learned spell (-1 = add, -2 = remove)
    "arm",         # Acquired ARM (-1 = add, -2 = remove)
    "fast_draw",   # Learned Fast Draw (-1 = add, -2 = remove)
    "tool",        # Acquired tool (-1 = add, -2 = remove)
]


# Parse and disassemble a recursive prefix expression,
# returning the tuple (length, string).
def parseExpression(data, offset, reloc = [], assignment = False):

    # Fetch opcode
    op = data[offset]
    length = 1

    opStr = exOpcodes[op]

    if op == 0x09:

        # Unary operator
        lhsLen, lhsStr = parseExpression(data, offset + 1, reloc)

        length += lhsLen
        str = "(" + lhsStr + " " + opStr + ")"

    elif op < 0x10:

        # Binary operator
        lhsLen, lhsStr = parseExpression(data, offset + 1, reloc)
        rhsLen, rhsStr = parseExpression(data, offset + 1 + lhsLen, reloc)

        length += lhsLen + rhsLen
        str = "(" + lhsStr + " " + opStr + " " + rhsStr + ")"

    elif op == 0x10:

        # Immediate value
        v = struct.unpack_from("<h", data, offset + 1)[0]

        length += 2
        str = "%d" % v

    elif op == 0x15:

        # Script address
        reloc.append(offset + 1)
        v = struct.unpack_from("<H", data, offset + 1)[0]

        length += 2
        str = "(addr %04x)" % v

    elif op in [0x12, 0x20]:

        # Simple variable
        str = opStr

    elif op in [0x11, 0x21]:

        # Assignable variable
        str = opStr

        if assignment:
            lhsLen, lhsStr = parseExpression(data, offset + 1, reloc)

            length += lhsLen
            str += " = " + lhsStr

    else:

        # Assignable indexed variable
        rhsLen, rhsStr = parseExpression(data, offset + 1, reloc)

        length += rhsLen
        str = opStr + "[" + rhsStr + "]"

        if assignment:
            lhsLen, lhsStr = parseExpression(data, offset + 1 + rhsLen, reloc)

            length += lhsLen
            str += " = " + lhsStr

    return length, str


#
# Script opcodes
#

Op = _enum(
    RETURN   =  0x00,  # return from subroutine
    CALL     =  0x01,  # call subroutine
    WINDOW   =  0x03,  # open message window
    CLOSE    =  0x04,  # close message window
    MESSAGE  =  0x06,  # message text
    ASSIGN   =  0x08,  # assignment
    JUMP     =  0x09,  # jump
    BREAK    =  0x0a,  # break from loop
    IF       =  0x0b,  # if statement
    WHILE    =  0x0c,  # loop statement
    WAIT     =  0x0e,  # wait
    SHOW     =  0x0f,  # show object
    HIDE     =  0x10,  # hide object
    ANIM     =  0x12,  # animate object
    MOVE     =  0x13,  # move object along path
    VFX      =  0x14,  # visual effect
    BATTLE   =  0x15,  # scripted battle
    MENU     =  0x16,  # display menu screen
    MAPFUNC  =  0x17,  # call map function
    EXEC     =  0x18,  # execute native code
    SOUND    =  0x21,  # play sound
    MUSIC    =  0x22,  # play music
    ENDING   =  0x24,  # show ending movie
    GAMEOVER =  0x27,  # return to load / new game screen

    ENTRY    = 0x100,  # pseudo-op for script entry address
    STRING   = 0x101,  # pseudo-op for string literal
    PTR      = 0x102,  # pseudo-op for bogus pointer
)

opcodes = [

    # length, mnemonic
    ( 1, "return"),
    ( 3, "call"),
    ( 1, "halt"),
    ( 2, "window"),  # variable length
    ( 1, "close"),
    ( 1, "{0x05}"),  # <unused>
    ( 1, "message"), # variable length
    ( 1, "{0x07}"),  # <unused>
    ( 1, "let"),     # contains expression
    ( 3, "jump"),
    ( 3, "break"),
    ( 1, "if"),      # contains expression
    ( 1, "while"),   # contains expression
    ( 7, "{0x0d}"),  # variable length
    ( 3, "wait"),    # variable length
    ( 3, "show"),
    ( 3, "hide"),
    (12, "{0x11}"),
    ( 6, "anim"),
    ( 5, "move"),    # variable length
    ( 2, "vfx"),     # variable length
    ( 8, "battle"),
    ( 2, "menu"),    # variable length
    ( 2, "mapfunc"),
    ( 5, "exec"),
    ( 4, "{0x19}"),  # variable length
    ( 2, "{0x1a}"),  # variable length
    (12, "{0x1b}"),
    ( 4, "{0x1c}"),
    ( 4, "{0x1d}"),  # variable length
    ( 7, "{0x1e}"),
    ( 4, "{0x1f}"),  # variable length
    (11, "{0x20}"),
    ( 4, "sound"),
    ( 4, "music"),
    ( 3, "{0x23}"),  # variable length
    ( 1, "ending"),
    ( 6, "{0x25}"),
    ( 1, "nop"),
    ( 1, "gameover"),
    ( 3, "{0x28}"),
]


# Object representing one script instruction.
#
# Attributes:
#   op     = opcode (int)
#   len    = instruction length in bytes
#   addr   = instruction start address
#   bytes  = instruction data bytes
#   disass = disassembled instruction (string)
#   reloc  = list of offsets (relative to start of instruction) to relocatable addresses within the instruction
class Instruction:

    # Create an instruction object.
    def __init__(self, op, length, addr, bytes, disass, reloc = []):
        self.op = op
        self.length = length
        self.addr = addr
        self.bytes = bytes
        self.disass = disass
        self.reloc = reloc

    # Get the text of MESSAGE and STRING instructions.
    # The text is encoded in the game character set and null-terminated.
    def getText(self):
        if self.op == Op.MESSAGE:
            return self.bytes[1:]
        elif self.op == Op.STRING:
            return self.bytes
        else:
            raise ValueError("getText() called for instruction " + self.disass)

    # Set the text of MESSAGE and STRING instructions.
    # The text must be encoded in the game character set and null-terminated.
    def setText(self, text):
        if self.op == Op.MESSAGE:
            self.bytes = bytearray([Op.MESSAGE]) + bytearray(text)
            self.length = len(self.bytes)
            self.disass = "message"
        elif self.op == Op.STRING:
            self.bytes = bytearray(text)
            self.length = len(self.bytes)
            self.disass = "string"
        else:
            raise ValueError("setText() called for instruction " + self.disass)

    # Relocate addresses within the instruction operands according to a
    # mapping of old to new addresses.
    def relocate(self, addrMap):
        for offset in self.reloc:
            oldAddr = struct.unpack_from("<H", self.bytes, offset)[0]
            newAddr = addrMap[oldAddr]

            # Target address 0xfffe for CALL is special
            if self.op == Op.CALL and newAddr == 0xfffe:
                raise ValueError("Target address of CALL instruction at %04x relocated to %04x" % (self.addr, newAddr))

            struct.pack_into("<H", self.bytes, offset, newAddr)


# Decode one instruction at the given offset in the data and return an
# Instruction object.
def parseInstruction(data, offset, version, basePointer = mapBasePointer, kanjiBitmap = None):

    # Fetch opcode
    op = data[offset]

    # The linker used for building the game has the habit
    # of inserting pointers to the current location in
    # some places. We need to skip these.
    p = struct.unpack_from("<L", data, offset)[0]

    if (offset % 4 == 0) and p == offset + 0x8014f000:
        return Instruction(Op.PTR, 4, offsetToAddr(offset, basePointer), data[offset:offset + 4], "<PTR>")

    # Heuristic for detecting string literals embedded within the code.
    # A more solid way would be to do a control flow analysis of the
    # code, or to look for the "addr" expression opcodes which reference
    # the strings.
    if (op == 0x05) or (op > 0x28) or (p == 0x20202020) or \
       ((op == 0x11) and (data[offset + 2] not in [0x00, 0xff])):

        end = data.index(b'\0', offset)
        length = end - offset + 1
        t = wa.text.decode(data[offset:end], version, kanjiBitmap)

        return Instruction(Op.STRING, length, offsetToAddr(offset, basePointer), data[offset:end + 1], "string " + t)

    # Regular instruction
    length, disass = opcodes[op]
    reloc = []

    # Get operand
    if op == Op.MESSAGE:

        # Operand is text until null byte
        end = data.index(b'\0', offset)
        disass += " " + wa.text.decode(data[offset + 1:end], version, kanjiBitmap)
        length = end - offset + 1

    elif op in [Op.CALL, Op.JUMP, Op.BREAK]:

        # Operand is a script address
        addr = struct.unpack_from("<H", data, offset + 1)[0]
        disass += " %04x" % addr

        # Target address 0xfffe for CALL is special
        if op != Op.CALL or addr != 0xfffe:
            reloc.append(1)

    elif op == Op.WINDOW:

        # Window type 3 has additional operands
        sel = data[offset + 1]
        disass += " %d" % sel

        if sel == 3:
            param = struct.unpack_from("<5H", data, offset + 2)
            disass += " type %d, x/y = (%d, %d), w/h = (%d, %d)" % param
            length += 10

    elif op == Op.ASSIGN:

        # Operand is an assignment expression
        exReloc = []
        exLen, exStr = parseExpression(data, offset + 1, exReloc, True)

        reloc += [(x - offset) for x in exReloc]

        disass += " " + exStr
        length += exLen

    elif op in [Op.IF, Op.WHILE]:

        # Operands are an expression followed by a script address
        exReloc = []
        exLen, exStr = parseExpression(data, offset + 1, exReloc)

        reloc += [(x - offset) for x in exReloc]
        reloc.append(1 + exLen)
        addr = struct.unpack_from("<H", data, offset + 1 + exLen)[0]

        disass += " " + exStr + (": (else jump %04x)" % addr)
        length += exLen + 2

    elif op == 0x0d:

        # Operand is variable
        sel = data[offset + 1]

        if sel in [0xfc, 0xfd, 0xfe]:
            length += 1

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == Op.WAIT:

        # Operand is variable
        sel = struct.unpack_from("<H", data, offset + 1)[0]

        if sel in [0xfff2, 0xfff3, 0xfff9, 0xfffc]:
            length += 2

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == Op.MOVE:

        # Operand is terminated by 0xfe/0xff
        end = offset + 3
        while data[end] not in [0xfe, 0xff]:
            end += 1

        length = end - offset + 1

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == Op.VFX:

        # Operand is variable
        sel = data[offset + 1]

        if sel == 0xf1:
            length += 5
        elif sel in [0xf4, 0xfd]:
            length += 6
        elif sel in [0xf5, 0xf6]:
            length += 3
        elif sel == 0xfb:
            length += 2
        elif sel == 0xff:
            length += 8

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == Op.MENU:

        # Operands depend on menu type
        sel = data[offset + 1]
        disass += " " + hex(sel)

        if sel == 0x01:
            disass += " (memory card)"
        elif sel == 0x02:
            disass += " (name entry)"
            length += 2
        elif sel == 0x03:
            disass += " (buy)"
            end = data.index(b'\xff', offset)
            length += end - offset - 1
        elif sel == 0x04:
            disass += " (sell)"
        elif sel == 0x07:
            disass += " (upgrade)"
        elif sel == 0x08:
            disass += " (create magic)"
            length += 1
        elif sel == 0x09:
            disass += " (load/save)"
            length += 1
        elif sel == 0x0a:
            disass += " (reload)"
        elif sel == 0x0e:
            disass += " (trial results)"
        elif sel == 0xff:
            disass += " (change)"

        if length > 2:
            disass += " " + " ".join(map(hex, data[offset + 2:offset + length]))

    elif op == Op.EXEC:

        # Operand is a pointer
        p = struct.unpack_from("<L", data, offset + 1)
        disass += " %08x" % p

    elif op in [0x19, 0x1d]:

        # Operand is variable
        sel = data[offset + 3]

        if sel == 0xff:
            length += 3

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == 0x1a:

        # Operand is variable
        sel = data[offset + 1]

        if sel in [0xfe, 0xff]:
            end = data.index(b'\xff\xff', offset + 2)
            length = end - offset + 2
        else:
            end = data.index(b'\xff', offset + 2)
            length = end - offset + 1

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == 0x1f:

        # Operand is variable
        sel = data[offset + 1]

        if sel != 0:
            length += 10

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    elif op == 0x23:

        # Operand is variable
        sel = data[offset + 2]

        if sel < 0x80:
            length += 6

        disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    else:
        if length > 1:
            disass += " " + " ".join(map(hex, data[offset + 1:offset + length]))

    return Instruction(op, length, offsetToAddr(offset, basePointer), data[offset:offset + length], disass, reloc)


# Recalculate all instruction addresses in a script to a new start address,
# creating a mapping of old to new addresses.
def recalcScriptAddr(script, startAddr):
    addrMap = {}
    newAddr = startAddr
    for instr in script:
        oldAddr = instr.addr
        instr.addr = newAddr
        addrMap[oldAddr] = newAddr
        newAddr = (newAddr + instr.length) & 0xffff

    return script, addrMap


# Fixup target addresses within the instructions of a script according to a
# mapping of old to new addresses.
def fixupScript(script, addrMap):
    for instr in script:
        instr.relocate(addrMap)

    return script


# Convert a list of script instructions to binary data.
def getScriptData(script):
    data = bytearray()
    for instr in script:
        data += instr.bytes

    return data


# Pad the size of a bytearray to a 32-bit boundary.
def align4(data):
    offset = len(data) % 4
    if offset:
        return data + bytearray(4 - offset)
    else:
        return data


# Map data section indexes
Section = _enum(
    ACTOR       =  5,
    ENTRY       =  6,  # script code entry table
    SCRIPT_1    =  7,  # first script code section
    SCRIPT_2    =  8,  # second script code section (optional)
    FLAG        =  9,  # flag byte
    KANJI       = 14,  # Kanji bitmap
    MUSIC_TABLE = 16,  # music offset table
    MUSIC_DATA  = 17,  # music data (VABs and LZSS-compressed SEQs)
)


# Object representing a aap data block.
class MapData:

    # Create a Map object from a data block.
    def __init__(self, mapBlock, mapNumber, version):
        self.version = version
        self.mapNumber = mapNumber

        self.setData(mapBlock)

    # Set the binary map data.
    def setData(self, mapBlock):
        self.data = bytearray(mapBlock)

        # Extract the pointer table at the start and convert the pointers
        # to offsets
        self.pointers = struct.unpack_from("<18L", self.data, 0x40)
        self.offsets = [pointerToOffset(p) for p in self.pointers]

        # Find the start and end of the main script entry table
        self.entryTableStart = self.offsets[Section.ENTRY]
        self.entryTableEnd = self.offsets[Section.SCRIPT_1]

        # Find the start and end of the first script section, which is
        # followed by either the second script code section (if present), or
        # the Kanji bitmap
        self.script1Start = self.offsets[Section.SCRIPT_1]
        if self.pointers[Section.SCRIPT_2]:
            self.script1End = self.offsets[Section.SCRIPT_2] - 4  # skip bogus pointer before next section
        else:
            self.script1End = self.offsets[Section.KANJI] - 4

        # Find the start and end of the optional second script section which
        # is followed by either the Kanji bitmap or, in maps 6 and 116, by
        # the music offset table
        if self.pointers[Section.SCRIPT_2]:
            self.script2Start = self.offsets[Section.SCRIPT_2]
            if self.pointers[Section.MUSIC_TABLE] < self.pointers[Section.KANJI]:
                self.script2End = self.offsets[Section.MUSIC_TABLE] - 4  # skip bogus pointer before next section
            else:
                self.script2End = self.offsets[Section.KANJI] - 4
        else:
            self.script2Start = None
            self.script2End = None

        # Each script code section is preceeded by an address table, the
        # first entry of which usually points to the first instruction after
        # the table
        if self.mapNumber in [37, 119]:
            firstAddr = struct.unpack_from("<H", self.data, self.script1Start + 2)[0]
        else:
            firstAddr = struct.unpack_from("<H", self.data, self.script1Start)[0]

        self.script1FirstInstr = addrToOffset(firstAddr)

        if self.script2Start is not None:
            firstAddr = struct.unpack_from("<H", self.data, self.script2Start)[0]
            self.script2FirstInstr = addrToOffset(firstAddr)

        # Extract the Kanji bitmap for decoding text in the JP version
        if self.pointers[Section.FLAG]:
            self.kanjiBitmap = self.data[self.offsets[Section.KANJI]:self.offsets[Section.FLAG]]
        elif self.pointers[10]:
            self.kanjiBitmap = self.data[self.offsets[Section.KANJI]:self.offsets[10]]
        else:
            self.kanjiBitmap = self.data[self.offsets[Section.KANJI]:self.offsets[Section.MUSIC_TABLE]]

        if len(self.kanjiBitmap) % 22:
            self.kanjiBitmap = self.kanjiBitmap[:-(len(self.kanjiBitmap) % 22)]

    # Extract an entry table from the given offset range.
    def _extractEntries(self, offset, endOffset):
        numEntries = (endOffset - offset) // 2
        return list(struct.unpack_from("<%dH" % numEntries, self.data, offset))

    # Extract the script entry table as a list of addresses.
    def getGlobalEntries(self):
        return self._extractEntries(self.entryTableStart, self.entryTableEnd)

    # Extract the entry table of the first script section as a list of addresses.
    def getScript1Entries(self):
        return self._extractEntries(self.script1Start, self.script1FirstInstr)

    # Extract the entry table of the second script section as a list of addresses.
    def getScript2Entries(self):
        if self.script2Start is None:
            return []
        else:
            return self._extractEntries(self.script2Start, self.script2FirstInstr)

    # Extract script code from the given offset range.
    def extractScript(self, offset, firstInstr, endOffset):
        script = []

        # Decode the entry table
        while offset < firstInstr:
            target = struct.unpack_from("<H", self.data, offset)[0]
            instr = Instruction(Op.ENTRY, 2, offsetToAddr(offset), self.data[offset:offset + 2], "entry %02x" % target, [0])
            script.append(instr)
            offset += 2

        # Decode the instructions
        while offset < endOffset:
            instr = parseInstruction(self.data, offset, self.version, mapBasePointer, self.kanjiBitmap)
            script.append(instr)
            offset += instr.length

        return script

    # Extract the first script section as a list of Instruction objects.
    def getScript1(self):
        return self.extractScript(self.script1Start, self.script1FirstInstr, self.script1End)

    # Extract the second script section as a list of Instruction objects.
    def getScript2(self):
        if self.script2Start is None:
            return []
        else:
            return self.extractScript(self.script2Start, self.script2FirstInstr, self.script2End)

    # Find the start and end of the MIPS code in the map data and return the
    # tuple (startOffset, endOffset).
    def _findMipsCode(self):

        # Finding the start of the code is somewhat tricky as there is no
        # direct section pointer to it.

        if self.pointers[10] > self.pointers[Section.MUSIC_TABLE]:

            # In maps 6 and 116, the code follows section 10 (which is
            # small) so we can get an estimate of the code start by taking
            # the start of that section
            startOffset = pointerToOffset(self.pointers[10])

        else:

            # For other maps, the code follows the music data section whose
            # last element is LZSS-compressed SEQ data; we obtain the start
            # of this data via the last entry in the music table and
            # calculate the size of the compressed data to find its end
            offset = self.offsets[Section.MUSIC_TABLE]

            while True:
                entry = struct.unpack_from("<L", self.data, offset)[0]
                if entry == 0xffffffff:
                    # End of table
                    break

                dataStart = self.offsets[Section.MUSIC_DATA] + entry
                offset += 4

            # The data starts with the uncompressed length
            startOffset = dataStart + wa.lzss.compressedSize(self.data[dataStart:])

            if startOffset % 4:
                startOffset += (4 - startOffset % 4)  # align to 32-bit boundary

        # We estimate the end offset of the code by the size of the text
        # section from the executable header at the start of the map data
        # (which is rounded to 2048 bytes so it's inexact, but that's good
        # enough for us)
        endOffset = struct.unpack_from("<L", self.data, 0x0c)[0]

        return startOffset, endOffset

    # Get a list of the strings in the MIPS code.
    def getCodeStrings(self):
        strings = []

        mapStringData = wa.data.mapStringData(self.version)
        if self.mapNumber in mapStringData:
            exeStart, exeEnd = self._findMipsCode()

            for offset, size in mapStringData[self.mapNumber]:
                end = self.data.index(b'\0', exeStart + offset)
                strings.append(self.data[exeStart + offset:end])

        return strings

    # Replace the script code and strings in the map data.
    def setScripts(self, script1, script2, codeStrings = []):

        # Remove bogus pointers from scripts because we don't want to
        # relocate and realign them, and they may cause problems during
        # script extraction when inserted unchanged
        script1 = [instr for instr in script1 if instr.op != Op.PTR]
        script2 = [instr for instr in script2 if instr.op != Op.PTR]

        # Copy all data preceding the entry table
        newData = self.data[0:self.entryTableStart]

        # Set the new starting addresses of the script sections
        script1, addrMap = recalcScriptAddr(script1, offsetToAddr(self.script1Start))

        end = addrToOffset(script1[-1].addr) + script1[-1].length
        if end % 4:
            end += 4 - (end % 4)  # align to 32-bit boundary

        self.script1End = end

        if script2:
            self.script2Start = self.script1End + 4
            struct.pack_into("<L", newData, 0x40 + Section.SCRIPT_2 * 4, offsetToPointer(self.script2Start))

            script2, addrMap2 = recalcScriptAddr(script2, offsetToAddr(self.script2Start))
            addrMap.update(addrMap2)

        # Create a new, relocated entry table and append it
        entries = self.getGlobalEntries()
        entryData = bytearray()

        for e in entries:
            try:
                newAddr = addrMap[e]
            except KeyError:
                newAddr = 0  # unused entry
            entryData.extend(struct.pack("<H", newAddr))

        newData.extend(entryData)

        # Relocate and append the first script section
        assert(len(newData) == self.script1Start)

        script1 = fixupScript(script1, addrMap)
        newData.extend(getScriptData(script1))
        newData = align4(newData)

        # Add bogus pointer before next section
        newData += struct.pack("<L", offsetToPointer(len(newData)))

        # Relocate and append the second script section
        if script2:
            assert(len(newData) == self.script2Start)

            script2 = fixupScript(script2, addrMap)
            newData.extend(getScriptData(script2))
            newData = align4(newData)

            self.script2End = len(newData)

            # Add bogus pointer before next section
            newData += struct.pack("<L", offsetToPointer(len(newData)))

        # Copy all following data up to the graphics at constant offset 0x15000
        assert(len(newData) % 4 == 0)

        gfxStart = 0x15000

        start = min(self.offsets[Section.MUSIC_TABLE], self.offsets[Section.KANJI])
        deltaOffset = len(newData) - start  # correction value for pointers and offsets due to changed script size

        newData.extend(self.data[start:gfxStart])
        if len(newData) > gfxStart:
            newData = newData[:gfxStart]
        elif len(newData) < gfxStart:
            newData.extend(bytearray(gfxStart - len(newData)))

        assert(len(newData) == gfxStart)

        # Find the start and end of the MIPS code in the original data
        exeStart, exeEnd = self._findMipsCode()

        # Relocate the code in the new data block. The MIPS's lack of 32-bit
        # operands to instructions doesn't help here... :-(
        # Luckily, the instruction sequences generated by the compiler used
        # by the game's developers are quite regular.
        startPointer = offsetToPointer(exeStart)
        endPointer = offsetToPointer(exeEnd)

        Reloc = _enum(
            POINTER = 0,  # 32-bit linear pointer
            JUMP    = 1,  # 26-bit jump instruction operand
            HILO    = 2,  # Upper 16 bits in first instruction, lower 16 bits (signed) in next instruction
            HILO_2  = 4,  # Upper 16 bits in first instruction, lower 16 bits (signed) in instruction after the next one
        )

        exeStart += deltaOffset
        exeEnd += deltaOffset

        if exeEnd > gfxStart:
            raise IndexError("Map data overrun")

        offset = exeStart
        while offset < exeEnd:

            # Read the next three instructions or data words
            w, w2, w3 = struct.unpack_from("<3L", newData, offset)

            relocType = None

            if (w >= startPointer) and w < (endPointer):

                # Regular pointer, for example in a jump table or in the
                # global vector
                relocType = Reloc.POINTER

            elif (w & 0xfc000000) in [0x08000000,   # j
                                      0x0c000000]:  # jal

                # Jump instruction with 26-bit operand
                a = ((w & 0x03ffffff) << 2) | 0x80000000
                if a >= startPointer and a <= endPointer:
                    relocType = Reloc.JUMP

            elif (w & 0xfc00fffc) == 0x3c008014:

                # First instruction is 'lui rx, 0x8014..0x8017'; examine the
                # next two instructions
                if (w2 & 0xfc000000) in [0x24000000,   # addiu
                                         0x84000000,   # lh
                                         0x8c000000,   # lw
                                         0x90000000,   # lbu
                                         0x94000000,   # lhu
                                         0xa0000000,   # sb
                                         0xa4000000,   # sh
                                         0xac000000]:  # sw

                    # Sequence is 'lui + addiu' for loading a 32-bit
                    # pointer, or 'lui + load/store' for accessing data
                    # at a fixed address
                    relocType = Reloc.HILO

                elif (w2 & 0xfc000000) == 0x34000000:

                    # Sequence is 'lui + ori' for loading a 32-bit pointer
                    # (never used for references withing the code, only for
                    # fixed addresses like the start of the map graphics)
                    relocType = None

                elif (w2 & 0xfc0007ff) == 0x00000021:  # addu

                    if (w3 & 0xfc000000) in [0x84000000,   # lh
                                             0x8c000000,   # lw
                                             0x90000000,   # lbu
                                             0x94000000,   # lhu
                                             0xa0000000,   # sb
                                             0xa4000000,   # sh
                                             0xac000000]:  # sw

                        # Sequence is 'lui + addu + load/store' for indexing
                        # an array
                        relocType = Reloc.HILO_2

                    else:
                        raise ValueError("Unrecognized MIPS instruction sequence %08x %08x %08x" % (w, w2, w3))

                else:
                    raise ValueError("Unrecognized MIPS instruction sequence %08x %08x %08x" % (w, w2, w3))

            if relocType == Reloc.POINTER:

                # Stuff in the new pointer
                n = w + deltaOffset
                struct.pack_into("<L", newData, offset, n)

            elif relocType == Reloc.JUMP:

                # Stuff in the new operand
                n = (w & 0xfc000000) | ((w & 0x03ffffff) + (deltaOffset // 4))
                struct.pack_into("<L", newData, offset, n)

            elif relocType == Reloc.HILO:

                # Combine the split pointer, adjust it, and write back the hi/lo halves
                p = ((w & 0xffff) << 16) + struct.unpack_from("<h", newData, offset + 4)[0]
                if (p >= startPointer) and (p <= mapGfxPointer):
                    p += deltaOffset

                    hi = p >> 16
                    lo = p & 0xffff
                    if lo >= 0x8000:
                        hi += 1  # adding a negative lower part will decrement the upper part

                    struct.pack_into("<H", newData, offset, hi)
                    struct.pack_into("<H", newData, offset + 4, lo)

            elif relocType == Reloc.HILO_2:

                # Combine the split pointer, adjust it, and write back the hi/lo halves
                p = ((w & 0xffff) << 16) + struct.unpack_from("<h", newData, offset + 8)[0]
                if (p >= startPointer) and (p <= mapGfxPointer):
                    p += deltaOffset

                    hi = p >> 16
                    lo = p & 0xffff
                    if lo >= 0x8000:
                        hi += 1  # adding a negative lower part will decrement the upper part

                    struct.pack_into("<H", newData, offset, hi)
                    struct.pack_into("<H", newData, offset + 8, lo)

            offset += 4

        # Insert the strings in the MIPS code
        if codeStrings:
            mapStringData = wa.data.mapStringData(self.version)[self.mapNumber]
            for i in range(len(codeStrings)):
                s = codeStrings[i]
                offset, maxSize = mapStringData[i]

                if len(s) < maxSize:
                    s += b'\0' * (maxSize - len(s))  # pad with null bytes

                newData[exeStart + offset:exeStart + offset + maxSize] = s

        # Update the remaining section pointers which follow the script code
        for section in [Section.FLAG, 10, 11, 12, 13, Section.KANJI, 15, Section.MUSIC_TABLE, Section.MUSIC_DATA]:
            offset = 0x40 + section * 4
            p = struct.unpack_from("<L", newData, offset)[0]
            if p:
                struct.pack_into("<L", newData, offset, p + deltaOffset)

        # Update addresses in EXEC instructions
        for instr in script1 + script2:
            if instr.op == Op.EXEC:
                offset = addrToOffset(instr.addr)
                p = struct.unpack_from("<L", newData, offset + 1)[0]
                struct.pack_into("<L", newData, offset + 1, p + deltaOffset)

        # Update pointers and offsets in the executable header
        for offset in [0, 12]:
            p = struct.unpack_from("<L", newData, offset)[0]
            struct.pack_into("<L", newData, offset, p + deltaOffset)

        # Copy graphics and sound data
        newData.extend(self.data[0x15000:])

        # Set the new data block
        self.setData(newData)
