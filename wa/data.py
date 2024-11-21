#
# wa.data - Wild Arms translation-related data tables
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

from .version import Version, isJapanese


#
# Translatable strings embedded in the main executable
#

# JP version
execFileData_JP = [

    # tableOffset, numStrings, dataOffset, dataSize, specialBytes, specialHack, transDir, transFileName
    ( 0xf4c,   6,   None,  0xb0, 0, False, "exe", "menu_help.txt"),
    (0x1018, 256,   None, 0x988, 1, False, "exe", "item.txt"),
    (0x1da4, 256,   None, 0xa38, 0, False, "exe", "item_help.txt"),
    (0x4fe8,   8,   None,  0x68, 1, False, "exe", "arm.txt"),
    (0x5074,   8,   None,  0xd0, 0, False, "exe", "arm_help.txt"),
    (0x51cc,  33,   None,  0xd8, 1, False, "exe", "fast_draw.txt"),
    (0x532c,  32,   None, 0x2f4, 0, False, "exe", "fast_draw_help.txt"),
    (0x5868,  46, 0x5ea0, 0x1f4, 1, False, "exe", "magic2.txt"),
    (0x6098,  64,   None, 0x668, 0, False, "exe", "magic_help.txt"),
    (0x6e0c,  18,   None,  0xa4, 0, False, "exe", "auto_cmd.txt"),
    (0x6efc,  18,   None,  0x7c, 0, False, "exe", "auto_cmd_help.txt"),
    (0x6fc8,   3,   None,   0xc, 0, False, "exe", "technique.txt"),
    (0x6fe8,  10,   None,  0x64, 3, False, "exe", "config.txt"),
    (0x7078,  10,   None,  0xa4, 0, False, "exe", "config_help.txt"),
    (0x7148,  31,   None,  0xec, 1,  True, "exe", "config_setting.txt"),
    (0x72b4,  12,   None,  0x64, 0, False, "exe", "menu.txt"),
    (0x734c,   2,   None,  0x14, 0, False, "exe", "menu2.txt"),
    (0x736c,  12,   None,  0x6c, 0, False, "exe", "tool.txt"),
    (0x740c,  12,   None, 0x104, 0, False, "exe", "tool_help.txt"),
    (0x7544, 128,   None, 0x26c, 0, False, "exe", "map_name.txt"),
    (0x840c,  20,   None, 0x22c, 1, False, "exe", "memory_card.txt"),
    (0x88ac,  21,   None,  0x80, 0, False, "exe", "icon.txt"),
    (0x8984,  10,   None,  0x70, 0, False, "exe", "window.txt"),
    (0x8a20,  22,   None, 0x174, 0, False, "exe", "load_save.txt"),
    (0x8e98,  13,   None,  0x50, 0, False, "exe", "controller.txt"),
    (0x9228,  70,   None, 0x3dc, 0, False, "exe", "battle.txt"),
    (0x9798, 256,   None, 0x734, 0, False, "exe", "enemy.txt"),
    (0xa2f0,  11,   None,  0xc4, 0, False, "exe", "command_help.txt"),
    (0xae20, 214,   None, 0x7b4, 1, False, "exe", "attack.txt"),
    (0xc53c,  13,   None,  0x78, 0, False, "exe", "force.txt"),
    (0xc5ec,  14,   None, 0x144, 0, False, "exe", "force_help.txt"),
    (0xc7e4,  21,   None,  0xd0, 1, False, "exe", "guardian.txt"),
]

execFileData2_JP1 = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xed8, 4,  19, None   , "exe", "job.txt"),
    (  0xf24, 5,   7, "ascii", "exe", "luck.txt"),
    ( 0x868c, 1, 520, None   , "exe", "name_entry.txt"),
    ( 0xe0e4, 1,  20, "ascii", "exe", "best_runners.txt"),
    ( 0xe0f8, 1,  20, "ascii", "exe", "trial_result.txt"),
    (0xbd7b0, 1,   8, "ascii", "exe", "miss.txt"),
    (0xbd7f0, 1,   4, "ascii", "exe", "ok.txt"),
]

execFileData2_JP2 = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xed8, 4,  19, None   , "exe", "job.txt"),
    (  0xf24, 5,   7, "ascii", "exe", "luck.txt"),
    ( 0x868c, 1, 520, None   , "exe", "name_entry.txt"),
    ( 0xe0e4, 1,  20, "ascii", "exe", "best_runners.txt"),
    ( 0xe0f8, 1,  20, "ascii", "exe", "trial_result.txt"),
    (0xcb52c, 1,   8, "ascii", "exe", "miss.txt"),
    (0xcb56c, 1,   4, "ascii", "exe", "ok.txt"),
]

# US version
execFileData_US = [

    # tableOffset, numStrings, dataOffset, dataSize, specialBytes, specialHack, transDir, transFileName
    ( 0xf54,   6,   None,  0xac, 0, False, "exe", "menu_help.txt"),
    (0x101c, 256,   None, 0xad8, 1, False, "exe", "item.txt"),
    (0x1ef8, 256,   None, 0xaac, 0, False, "exe", "item_help.txt"),
    (0x51b0,   8,   None,  0x58, 1, False, "exe", "arm.txt"),
    (0x522c,   8,   None,  0xbc, 0, False, "exe", "arm_help.txt"),
    (0x5370,  33,   None,  0xdc, 1, False, "exe", "fast_draw.txt"),
    (0x54d4,  32,   None, 0x2e8, 0, False, "exe", "fast_draw_help.txt"),
    (0x5a04,  46, 0x5f22, 0x1d2, 1, False, "exe", "magic2.txt"),
    (0x60f8,  64,   None, 0x5c8, 0, False, "exe", "magic_help.txt"),
    (0x6dcc,  18,   None,  0x94, 0, False, "exe", "auto_cmd.txt"),
    (0x6eac,  18,   None,  0xac, 0, False, "exe", "auto_cmd_help.txt"),
    (0x6fa4,   3,   None,  0x18, 0, False, "exe", "technique.txt"),
    (0x6fcc,  10,   None,  0x64, 3, False, "exe", "config.txt"),
    (0x705c,  10,   None,  0xc8, 0, False, "exe", "config_help.txt"),
    (0x7150,  31,   None, 0x104, 1,  True, "exe", "config_setting.txt"),
    (0x72d4,  12,   None,  0x84, 0, False, "exe", "menu.txt"),
    (0x738c,   2,   None,  0x18, 0, False, "exe", "menu2.txt"),
    (0x73b0,  12,   None,  0x50, 0, False, "exe", "tool.txt"),
    (0x7434,  12,   None, 0x110, 0, False, "exe", "tool_help.txt"),
    (0x7578, 128,   None, 0x330, 0, False, "exe", "map_name.txt"),
    (0x8508,  20,   None, 0x280, 1, False, "exe", "memory_card.txt"),
    (0x883c,  21,   None,  0x74, 0, False, "exe", "icon.txt"),
    (0x8908,  10,   None,  0x5c, 0, False, "exe", "window.txt"),
    (0x8990,  22,   None, 0x154, 0, False, "exe", "load_save.txt"),
    (0x8de8,  13,   None,  0x58, 0, False, "exe", "controller.txt"),
    (0x918c,  70,   None, 0x4f4, 0, False, "exe", "battle.txt"),
    (0x9814, 256,   None, 0x7a4, 0, False, "exe", "enemy.txt"),
    (0xa3e0,  11,   None,  0xdc, 0, False, "exe", "command_help.txt"),
    (0xaf28, 214,   None, 0xa34, 1, False, "exe", "attack.txt"),
    (0xc8c4,  13,   None,  0xa4, 0, False, "exe", "force.txt"),
    (0xc9a0,  14,   None, 0x184, 0, False, "exe", "force_help.txt"),
    (0xcbd8,  21,   None,  0xe0, 1, False, "exe", "guardian.txt"),
]

execFileData2_US = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xee0, 4, 19, None, "exe", "job.txt"),
    (  0xf2c, 5,  7, None, "exe", "luck.txt"),
    ( 0x87dc, 1, 92, None, "exe", "name_entry.txt"),
    ( 0x8ed2, 1, 18, None, "exe", "best_runners.txt"),
    ( 0xe4dc, 1, 20, None, "exe", "trial_result.txt"),
    (0xc1c48, 1,  8, None, "exe", "miss.txt"),
    (0xc1c90, 1,  4, None, "exe", "ok.txt"),
]

# EN version
execFileData_EN = [

    # tableOffset, numStrings, dataOffset, dataSize, specialBytes, specialHack, transDir, transFileName
    ( 0xf4c,   6,   None,  0xac, 0, False, "exe", "menu_help.txt"),
    (0x1014, 256,   None, 0xad8, 1, False, "exe", "item.txt"),
    (0x1ef0, 256,   None, 0xaac, 0, False, "exe", "item_help.txt"),
    (0x51a8,   8,   None,  0x58, 1, False, "exe", "arm.txt"),
    (0x5224,   8,   None,  0xbc, 0, False, "exe", "arm_help.txt"),
    (0x5368,  33,   None,  0xdc, 1, False, "exe", "fast_draw.txt"),
    (0x54cc,  32,   None, 0x2e8, 0, False, "exe", "fast_draw_help.txt"),
    (0x59fc,  46, 0x5f1a, 0x1d2, 1, False, "exe", "magic2.txt"),
    (0x60f0,  64,   None, 0x5c8, 0, False, "exe", "magic_help.txt"),
    (0x6dc4,  18,   None,  0x94, 0, False, "exe", "auto_cmd.txt"),
    (0x6ea4,  18,   None,  0xac, 0, False, "exe", "auto_cmd_help.txt"),
    (0x6f9c,   3,   None,  0x18, 0, False, "exe", "technique.txt"),
    (0x6fc4,  10,   None,  0x64, 3, False, "exe", "config.txt"),
    (0x7054,  10,   None,  0xc8, 0, False, "exe", "config_help.txt"),
    (0x7148,  31,   None, 0x104, 1,  True, "exe", "config_setting.txt"),
    (0x72cc,  12,   None,  0x84, 0, False, "exe", "menu.txt"),
    (0x7384,   2,   None,  0x18, 0, False, "exe", "menu2.txt"),
    (0x73a8,  12,   None,  0x50, 0, False, "exe", "tool.txt"),
    (0x742c,  12,   None, 0x110, 0, False, "exe", "tool_help.txt"),
    (0x7570, 128,   None, 0x330, 0, False, "exe", "map_name.txt"),
    (0x8500,  20,   None, 0x278, 1, False, "exe", "memory_card.txt"),
    (0x882c,  21,   None,  0x74, 0, False, "exe", "icon.txt"),
    (0x88f8,  10,   None,  0x5c, 0, False, "exe", "window.txt"),
    (0x8980,  22,   None, 0x14c, 0, False, "exe", "load_save.txt"),
    (0x8dd0,  13,   None,  0x58, 0, False, "exe", "controller.txt"),
    (0x8f18,   6,   None,  0x58, 0, False, "exe", "load_save2.txt"),
    (0x9230,  70,   None, 0x4f4, 0, False, "exe", "battle.txt"),
    (0x98b8, 256,   None, 0x7a4, 0, False, "exe", "enemy.txt"),
    (0xa484,  11,   None,  0xdc, 0, False, "exe", "command_help.txt"),
    (0xafcc, 214,   None, 0xa34, 1, False, "exe", "attack.txt"),
    (0xc968,  13,   None,  0xa4, 0, False, "exe", "force.txt"),
    (0xca44,  14,   None, 0x184, 0, False, "exe", "force_help.txt"),
    (0xcc7c,  21,   None,  0xe0, 1, False, "exe", "guardian.txt"),
]

execFileData2_EN = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xed8, 4, 19, None, "exe", "job.txt"),
    (  0xf24, 5,  7, None, "exe", "luck.txt"),
    ( 0x87cc, 1, 92, None, "exe", "name_entry.txt"),
    ( 0x8eba, 1, 18, None, "exe", "best_runners.txt"),
    ( 0xe580, 1, 20, None, "exe", "trial_result.txt"),
    (0xc1a80, 1,  8, None, "exe", "miss.txt"),
    (0xc1ac8, 1,  4, None, "exe", "ok.txt"),
]

# DE version
execFileData_DE = [

    # tableOffset, numStrings, dataOffset, dataSize, specialBytes, specialHack, transDir, transFileName
    ( 0xf44,   6,   None,  0xbc, 0, False, "exe", "menu_help.txt"),
    (0x101c, 256,   None, 0xa9c, 1, False, "exe", "item.txt"),
    (0x1ebc, 256,   None, 0xae0, 0, False, "exe", "item_help.txt"),
    (0x51a8,   8,   None,  0x58, 1, False, "exe", "arm.txt"),
    (0x5224,   8,   None,  0xbc, 0, False, "exe", "arm_help.txt"),
    (0x5368,  33,   None,  0xdc, 1, False, "exe", "fast_draw.txt"),
    (0x54cc,  32,   None, 0x2d8, 0, False, "exe", "fast_draw_help.txt"),
    (0x59ec,  46, 0x6024, 0x20c, 1, False, "exe", "magic2.txt"),
    (0x6238,  64,   None, 0x5f8, 0, False, "exe", "magic_help.txt"),
    (0x6f3c,  18,   None,  0x98, 0, False, "exe", "auto_cmd.txt"),
    (0x7020,  18,   None,  0xb0, 0, False, "exe", "auto_cmd_help.txt"),
    (0x711c,   3,   None,  0x1c, 0, False, "exe", "technique.txt"),
    (0x7148,  10,   None,  0x64, 3, False, "exe", "config.txt"),
    (0x71d8,  10,   None,  0xdc, 0, False, "exe", "config_help.txt"),
    (0x72e0,  31,   None, 0x114, 1,  True, "exe", "config_setting.txt"),
    (0x7474,  12,   None,  0x7c, 0, False, "exe", "menu.txt"),
    (0x7524,   2,   None,  0x18, 0, False, "exe", "menu2.txt"),
    (0x7548,  12,   None,  0x58, 0, False, "exe", "tool.txt"),
    (0x75d4,  12,   None, 0x10c, 0, False, "exe", "tool_help.txt"),
    (0x7714, 128,   None, 0x30c, 0, False, "exe", "map_name.txt"),
    (0x8680,  20,   None, 0x344, 1, False, "exe", "memory_card.txt"),
    (0x8a78,  21,   None,  0x88, 0, False, "exe", "icon.txt"),
    (0x8b58,  10,   None,  0x54, 0, False, "exe", "window.txt"),
    (0x8bd8,  22,   None, 0x19c, 0, False, "exe", "load_save.txt"),
    (0x9078,  13,   None,  0x6c, 0, False, "exe", "controller.txt"),
    (0x91d4,   6,   None,  0x64, 0, False, "exe", "load_save2.txt"),
    (0x94e8,  70,   None, 0x4e8, 0, False, "exe", "battle.txt"),
    (0x9b64, 256,   None, 0x7b8, 0, False, "exe", "enemy.txt"),
    (0xa744,  11,   None,  0xe0, 0, False, "exe", "command_help.txt"),
    (0xb290, 214,   None, 0xaa0, 1, False, "exe", "attack.txt"),
    (0xcc98,  13,   None,  0x9c, 0, False, "exe", "force.txt"),
    (0xcd6c,  14,   None, 0x180, 0, False, "exe", "force_help.txt"),
    (0xcfa0,  21,   None,  0xe0, 1, False, "exe", "guardian.txt"),
]

execFileData2_DE = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xed0, 4, 19, None, "exe", "job.txt"),
    (  0xf1c, 5,  7, None, "exe", "luck.txt"),
    ( 0x8a18, 1, 92, None, "exe", "name_entry.txt"),
    ( 0x9176, 1, 18, None, "exe", "best_runners.txt"),
    ( 0xe8a4, 1, 20, None, "exe", "trial_result.txt"),
    (0xc1f8c, 1,  8, None, "exe", "miss.txt"),
    (0xc1fd4, 1,  4, None, "exe", "ok.txt"),
]

# EN version
execFileData_ES = [

    # tableOffset, numStrings, dataOffset, dataSize, specialBytes, specialHack, transDir, transFileName
    ( 0xf44,   6,   None,  0xb0, 0, False, "exe", "menu_help.txt"),
    (0x1010, 256,   None, 0xa18, 1, False, "exe", "item.txt"),
    (0x1e2c, 256,   None, 0xa6c, 0, False, "exe", "item_help.txt"),
    (0x50a4,   8,   None,  0x60, 1, False, "exe", "arm.txt"),
    (0x5128,   8,   None,  0x98, 0, False, "exe", "arm_help.txt"),
    (0x5248,  33,   None,  0xd0, 1, False, "exe", "fast_draw.txt"),
    (0x53a0,  32,   None, 0x2b4, 0, False, "exe", "fast_draw_help.txt"),
    (0x589c,  46, 0x5ed4, 0x1d4, 1, False, "exe", "magic2.txt"),
    (0x60ac,  64,   None, 0x5ec, 0, False, "exe", "magic_help.txt"),
    (0x6da4,  18,   None,  0x98, 0, False, "exe", "auto_cmd.txt"),
    (0x6e88,  18,   None,  0xa4, 0, False, "exe", "auto_cmd_help.txt"),
    (0x6f78,   3,   None,  0x1c, 0, False, "exe", "technique.txt"),
    (0x6fa4,  10,   None,  0x68, 3, False, "exe", "config.txt"),
    (0x7038,  10,   None,  0xc0, 0, False, "exe", "config_help.txt"),
    (0x7124,  31,   None, 0x100, 1,  True, "exe", "config_setting.txt"),
    (0x72a4,  12,   None,  0x74, 0, False, "exe", "menu.txt"),
    (0x734c,   2,   None,  0x1c, 0, False, "exe", "menu2.txt"),
    (0x7374,  12,   None,  0x58, 0, False, "exe", "tool.txt"),
    (0x7400,  12,   None, 0x10c, 0, False, "exe", "tool_help.txt"),
    (0x7540, 128,   None, 0x334, 0, False, "exe", "map_name.txt"),
    (0x84d4,  20,   None, 0x298, 1, False, "exe", "memory_card.txt"),
    (0x8820,  21,   None,  0x88, 0, False, "exe", "icon.txt"),
    (0x8900,  10,   None,  0x58, 0, False, "exe", "window.txt"),
    (0x8984,  22,   None, 0x164, 0, False, "exe", "load_save.txt"),
    (0x8dec,  13,   None,  0x5c, 0, False, "exe", "controller.txt"),
    (0x8f38,   6,   None,  0x68, 0, False, "exe", "load_save2.txt"),
    (0x925c,  70,   None, 0x4c4, 0, False, "exe", "battle.txt"),
    (0x98b4, 256,   None, 0x79c, 0, False, "exe", "enemy.txt"),
    (0xa474,  11,   None,  0xd8, 0, False, "exe", "command_help.txt"),
    (0xafb8, 214,   None, 0x9a8, 1, False, "exe", "attack.txt"),
    (0xc8c8,  13,   None,  0xac, 0, False, "exe", "force.txt"),
    (0xc9ac,  14,   None, 0x180, 0, False, "exe", "force_help.txt"),
    (0xcbdc,  21,   None,  0xe0, 1, False, "exe", "guardian.txt"),
]

execFileData2_ES = [

    # offset, numStrings, maxStringLen, encoding, transDir, transFileName
    (  0xed0, 4, 19, None, "exe", "job.txt"),
    (  0xf1c, 5,  7, None, "exe", "luck.txt"),
    ( 0x87c0, 1, 92, None, "exe", "name_entry.txt"),
    ( 0x8eda, 1, 18, None, "exe", "best_runners.txt"),
    ( 0xe4e0, 1, 20, None, "exe", "trial_result.txt"),
    (0xc1bc8, 1,  8, None, "exe", "miss.txt"),
    (0xc1c10, 1,  4, None, "exe", "ok.txt"),
]


def execFileData(version):
    if isJapanese(version):
        return execFileData_JP
    elif version == Version.US:
        return execFileData_US
    elif version == Version.EN:
        return execFileData_EN
    elif version == Version.DE:
        return execFileData_DE
    elif version == Version.ES:
        return execFileData_ES
    else:
        return None

def execFileData2(version):
    if version == Version.JP1:
        return execFileData2_JP1
    elif version == Version.JP2:
        return execFileData2_JP2
    elif version == Version.US:
        return execFileData2_US
    elif version == Version.EN:
        return execFileData2_EN
    elif version == Version.DE:
        return execFileData2_DE
    elif version == Version.ES:
        return execFileData2_ES
    else:
        return None

def mapNameTableOffset(version):
    if isJapanese(version):
        return 0x7544
    elif version == Version.US:
        return 0x7578
    elif version == Version.EN:
        return 0x7570
    elif version == Version.DE:
        return 0x7714
    elif version == Version.ES:
        return 0x7540
    else:
        return None


#
# Translatable strings embedded in the UT0.OVR overlay
#

# JP version
utilFileData_JP1 = [

    # tableOffset, numStrings, dataOffset, dataSize, maxStringLen, transDir, transFileName
    (0xe778, 64,   0x0, 0x3a8, 21, "exe", "magic.txt"),
    (0xe878,  4, 0x3a8,  0x28, 17, "exe", "character.txt"),
]

utilFileData_JP2 = [

    # tableOffset, numStrings, dataOffset, dataSize, maxStringLen, transDir, transFileName
    (0xe784, 64,   0x0, 0x3a8, 21, "exe", "magic.txt"),
    (0xe884,  4, 0x3a8,  0x28, 17, "exe", "character.txt"),
]

# US version
utilFileData_US = [

    # tableOffset, numStrings, dataOffset, dataSize, maxStringLen, transDir, transFileName
    (0xe23c, 64,   0x0, 0x278, 11, "exe", "magic.txt"),
    (0xe33c,  4, 0x278,  0x20,  9, "exe", "character.txt"),
]

# EN version
utilFileData_EN = [

    # tableOffset, numStrings, dataOffset, dataSize, maxStringLen, transDir, transFileName
    (0xd9b0, 64,   0x0, 0x278, 11, "exe", "magic.txt"),
    (0xdab0,  4, 0x278,  0x20,  9, "exe", "character.txt"),
]

# DE version
utilFileData_DE = [

    # tableOffset, numStrings, dataOffset, dataBytes, maxStringLen, transDir, transFileName
    (0xd9a0, 64,   0x0, 0x278, 11, "exe", "magic.txt"),
    (0xdaa0,  4, 0x278,  0x20,  9, "exe", "character.txt"),
]

# ES version
utilFileData_ES = [

    # tableOffset, numStrings, dataOffset, dataSize, maxStringLen, transDir, transFileName
    (0xd9a8, 64,   0x0, 0x284, 11, "exe", "magic.txt"),
    (0xdaa8,  4, 0x284,  0x20,  9, "exe", "character.txt"),
]


def utilFileData(version):
    if version == Version.JP1:
        return utilFileData_JP1
    elif version == Version.JP2:
        return utilFileData_JP2
    elif version == Version.US:
        return utilFileData_US
    elif version == Version.EN:
        return utilFileData_EN
    elif version == Version.DE:
        return utilFileData_DE
    elif version == Version.ES:
        return utilFileData_ES
    else:
        return None


#
# Translatable strings embedded in the MIPS code of maps
#

# JP version
mapStringData_JP = {

    # mapNumber -> [(offset, size)]
     5: [(0, 12), (12, 8), (20, 12), (32, 12), (44, 12)],
    36: [(16, 16)],
    51: [(0, 20)],
    57: [(0, 20)],
}

# Other versions
mapStringData_INT = {

    # mapNumber -> [(offset, size)]
     5: [(0, 8), (8, 8), (16, 8), (24, 8), (32, 12)],
    36: [(16, 8)],
    51: [(0, 12)],
    57: [(0, 12)],
}


def mapStringData(version):
    if isJapanese(version):
        return mapStringData_JP
    else:
        return mapStringData_INT


#
# Fonts in the main executable
#

# JP version
fontData_JP1 = [

    # offset, numChars, charWidth, charHeight, lineSpacing, outCharsPerRow, transDir, transFileName
    ( 0xe10c, 465, 12, 11, 1, 32, "gfx", "kanji.png"),
    (0xc120c, 524, 12, 11, 1, 32, "gfx", "dialog_font.png"),
]

fontData_JP2 = [

    # offset, numChars, charWidth, charHeight, lineSpacing, outCharsPerRow, transDir, transFileName
    ( 0xe10c, 465, 12, 11, 1, 32, "gfx", "kanji.png"),
    (0xc0e04, 524, 12, 11, 1, 32, "gfx", "dialog_font.png"),
]

# US version
fontData_US = [

    # offset, numChars, charWidth, charHeight, lineSpacing, outCharsPerRow, transDir, transFileName
    (0xe4f0, 96, 8, 16, 0, 16, "gfx", "dialog_font.png"),
    (0xeaf0, 96, 8, 16, 0, 16, "gfx", "dialog_font2.png"),
    (0xf0f0, 96, 8, 16, 0, 16, "gfx", "dialog_font3.png"),
    (0xf6f0, 96, 8, 16, 0, 16, "gfx", "dialog_font4.png"),
]

# EN version
fontData_EN = [

    # offset, numChars, charWidth, charHeight, outCharsPerRow, transDir, transFileName
    (0xe594, 224, 8, 16, 0, 16, "gfx", "dialog_font.png"),
]

# DE version
fontData_DE = [

    # offset, numChars, charWidth, charHeight, outCharsPerRow, transDir, transFileName
    (0xe8b8, 224, 8, 16, 0, 16, "gfx", "dialog_font.png"),
]

# ES version
fontData_ES = [

    # offset, numChars, charWidth, charHeight, outCharsPerRow, transDir, transFileName
    (0xe4f4, 224, 8, 16, 0, 16, "gfx", "dialog_font.png"),
]


def fontData(version):
    if version == Version.JP1:
        return fontData_JP1
    elif version == Version.JP2:
        return fontData_JP2
    elif version == Version.US:
        return fontData_US
    elif version == Version.EN:
        return fontData_EN
    elif version == Version.DE:
        return fontData_DE
    elif version == Version.ES:
        return fontData_ES
    else:
        return None


#
# Script code in the main executable
#

# JP version
execScriptData_JP = (

    # tableOffset, numScripts, dataOffset, dataSize
    0x8f80, 10, 0x9078, 0x1ac
)

# US version
execScriptData_US = (

    # tableOffset, numScripts, dataOffset, dataSize
    0x8ee8, 10, 0x8fe0, 0x1a8
)

# EN version
execScriptData_EN = (

    # tableOffset, numScripts, dataOffset, dataSize
    0x8f8c, 10, 0x9084, 0x1a8
)

# DE version
execScriptData_DE = (

    # tableOffset, numScripts, dataOffset, dataSize
    0x9254, 10, 0x934c, 0x198
)

# ES version
execScriptData_ES = (

    # tableOffset, numScripts, dataOffset, dataSize
    0x8fbc, 10, 0x90b4, 0x1a4
)


def execScriptData(version):
    if isJapanese(version):
        return execScriptData_JP
    elif version == Version.US:
        return execScriptData_US
    elif version == Version.EN:
        return execScriptData_EN
    elif version == Version.DE:
        return execScriptData_DE
    elif version == Version.ES:
        return execScriptData_ES
    else:
        return None



#
# Textures in archive files
#

textureData = [

    # subDir, fileName, archiveSize, lastSectionSize, textureList
    ("SYS", "UT0.BIN", None, 0x200, [

        # pixelSection, clutSection, dimensions, clutOffset, transFileName
        (1, 0, (256, 256),  0, "memory_card.png"),
        (3, 2, (256, 256),  0, "name_entry.png"),
        (5, 4, (256, 256), 32, "load_save.png"),
    ]),

    ("SYS", "SY0.BIN", 0xb000, -1, [
        (1, 0, (256, 256), 0x1c0, "menu_font.png"),
        (2, 0, (256, 256), 0x260, "menu_labels.png"),
    ]),

    ("SYS", "SY1.BIN", 0xb000, -1, [
        (1, 0, (256, 256), 0x1c0, "menu_font.png"),
        (2, 0, (256, 256), 0x260, "menu_labels.png"),
    ]),
]
