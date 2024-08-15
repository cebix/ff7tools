#
# ff7.data - Final Fantasy VII translation-related data tables
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import ff7


#
# Kernel string list information (KERNEL.BIN archive)
#

kernelStringData = [

    # index, numStrings, compressed, transDir, transFileName
    ( 0,  32, True,  "kernel", "command_help.txt"),
    ( 1, 256, True,  "kernel", "ability_help.txt"),
    ( 2, 128, True,  "kernel", "item_help.txt"),
    ( 3, 128, True,  "kernel", "weapon_help.txt"),
    ( 4,  32, True,  "kernel", "armor_help.txt"),
    ( 5,  32, True,  "kernel", "accessory_help.txt"),
    ( 6,  96, True,  "kernel", "materia_help.txt"),
    ( 7,  64, True,  "kernel", "key_item_help.txt"),
    ( 8,  32, False, "kernel", "command.txt"),
    ( 9, 256, False, "kernel", "ability.txt"),
    (10, 128, False, "kernel", "item.txt"),
    (11, 128, False, "kernel", "weapon.txt"),
    (12,  32, False, "kernel", "armor.txt"),
    (13,  32, False, "kernel", "accessory.txt"),
    (14,  96, False, "kernel", "materia.txt"),
    (15,  64, False, "kernel", "key_item.txt"),
    (16, 128, True,  "kernel", "battle.txt"),
    (17,  16, False, "kernel", "summon.txt"),
]


#
# Translatable strings embedded in executable files
#

# English PAL version
execFileData_EN = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x39914, 0x0c, 23, False, "menu", "main.txt"),
        (0x39a5c, 0x08,  3, True,  "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts use the 8x8 font with Japanese encoding
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1ae8, 0x30, 51, False, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x82a4, 0x0c, 23, False, "menu", "equip_attr_short.txt"),
        (0x83f8, 0x0a,  9, False, "menu", "element.txt"),
        (0x8454, 0x24,  4, False, "menu", "remove.txt"),
        (0x84e4, 0x14,  6, False, "menu", "materia.txt"),
        (0x8570, 0x14, 35, False, "menu", "materia2.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1cfc, 0x26,  6, False, "menu", "form1.txt"),
        (0x1de0, 0x16, 26, False, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x3260, 0x22, 25, False, "menu", "lv4_limit.txt"),
        (0x3cd4, 0x0c, 11, False, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x2128, 0x24, 14, False, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x2934, 0x14, 14, False, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e6c, 0x0c, 10, False, "menu", "default_name.txt"),
        (0x8ee4, 0x08,  8, False, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xeedc, 0x08,  1, False, "menu", "save1.txt"),
        (0x12cfc, 0x24, 38, False, "menu", "save2.txt"),
        (0x13260, 0x30, 20, False, "menu", "save3.txt"),
        (0x13684, 0x06,  1, False, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x42d4, 0x14,  9, False, "menu", "shop_type.txt"),
        (0x4388, 0x2e,  8, False, "menu", "shop_greeting1.txt"),
        (0x4554, 0x2e,  8, False, "menu", "shop_greeting2.txt"),
        (0x6160, 0x0a,  9, False, "menu", "element.txt"),
        (0x61bc, 0x24,  4, False, "menu", "remove.txt"),
        (0x624c, 0x14,  6, False, "menu", "materia.txt"),
        (0x62d8, 0x14, 35, False, "menu", "materia2.txt"),
        (0x6598, 0x16, 23, False, "menu", "equip_attr.txt"),
        (0x6798, 0x14, 10, False, "menu", "shop.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x196c, 0x0a,  9, False, "menu", "element.txt"),
        (0x19c8, 0x14, 27, False, "menu", "status.txt"),
        (0x1be4, 0x0f, 27, False, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x5315c, 0x08,  1, False, "battle", "pause.txt"),
        (0x53198, 0x0a, 32, False, "battle", "status.txt"),
        (0x5330c, 0x1c,  1, False, "battle", "gil1.txt"),
        (0x53328, 0x04,  1, False, "battle", "gil2.txt"),
        (0x5332c, 0x08,  1, False, "battle", "gil3.txt"),
        (0x53334, 0x0c,  1, False, "battle", "gil4.txt"),
        (0x53480, 0x0c,  1, False, "battle", "arena1.txt"),
        (0x5348c, 0x18,  1, False, "battle", "arena2.txt"),
        (0x534a4, 0x16,  5, False, "battle", "arena3.txt"),
        (0x5351c, 0x20, 24, False, "battle", "arena_handicap.txt"),
        (0x5383c, 0x22,  3, False, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x122dc, 0x06,  1, False, "chocobo", "black.txt"),
        (0x12400, 0x10, 24, False, "chocobo", "prices.txt"),
        (0x12580, 0x08, 44, False, "chocobo", "names.txt"),
    ]),
]

# French PAL version
execFileData_FR = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x39944, 0x14, 23, False, "menu", "main.txt"),
        (0x39b44, 0x08,  3, True,  "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts use the 8x8 font with Japanese encoding
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1b2c, 0x44, 51, False, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x8354, 0x14, 23, False, "menu", "equip_attr.txt"),
        (0x8568, 0x0a,  9, False, "menu", "element.txt"),
        (0x85c4, 0x22,  4, False, "menu", "remove.txt"),
        (0x864c, 0x1a, 42, False, "menu", "materia.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1cfc, 0x26,  6, False, "menu", "form1.txt"),
        (0x1de0, 0x16, 26, False, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x325c, 0x3c, 25, False, "menu", "lv4_limit.txt"),
        (0x3f58, 0x0e, 11, False, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x2128, 0x28, 14, False, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x293c, 0x1a, 14, False, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e6c, 0x0c, 10, False, "menu", "default_name.txt"),
        (0x8ee4, 0x0c,  8, False, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xef1c, 0x0c,  1, False, "menu", "save1.txt"),
        (0x12d48, 0x32, 37, False, "menu", "save2.txt"),
        (0x13490, 0x40, 20, False, "menu", "save3.txt"),
        (0x13a04, 0x08,  1, False, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x4398, 0x14,  9, False, "menu", "shop_type.txt"),
        (0x444c, 0x2e,  8, False, "menu", "shop_greeting1.txt"),
        (0x4ac4, 0x2e,  8, False, "menu", "shop_greeting2.txt"),
        (0x6b7c, 0x0a,  9, False, "menu", "element.txt"),
        (0x6bd8, 0x22,  4, False, "menu", "remove.txt"),
        (0x6c60, 0x1a, 42, False, "menu", "materia.txt"),
        (0x70a8, 0x1e,  5, False, "menu", "shop_menu.txt"),
        (0x7140, 0x18, 10, False, "menu", "shop.txt"),
        (0x7230, 0x16, 23, False, "menu", "equip_attr.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x1960, 0x0a,  9, False, "menu", "element.txt"),
        (0x19bc, 0x14, 27, False, "menu", "status.txt"),
        (0x1bd8, 0x1a, 27, False, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x5315c, 0x08,  1, False, "battle", "pause.txt"),
        (0x53198, 0x14, 32, False, "battle", "status.txt"),
        (0x5344c, 0x18,  1, False, "battle", "gil1.txt"),
        (0x53464, 0x04,  1, False, "battle", "gil2.txt"),
        (0x53468, 0x08,  1, False, "battle", "gil3.txt"),
        (0x53470, 0x10,  1, False, "battle", "gil4.txt"),
        (0x535c0, 0x0c,  1, False, "battle", "arena1.txt"),
        (0x535cc, 0x20,  1, False, "battle", "arena2.txt"),
        (0x535ec, 0x24,  5, False, "battle", "arena3.txt"),
        (0x5369c, 0x20, 24, False, "battle", "arena_handicap.txt"),
        (0x539bc, 0x22,  3, False, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x12ba8, 0x06,  1, False, "chocobo", "black.txt"),
        (0x12ccc, 0x12, 24, False, "chocobo", "prices.txt"),
        (0x12e7c, 0x0a, 39, False, "chocobo", "names.txt"),
    ]),
]

# German PAL version
execFileData_DE = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x39930, 0x12, 23, False, "menu", "main.txt"),
        (0x39b04, 0x08,  3, True,  "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts use the 8x8 font with Japanese encoding
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1b3c, 0x36, 51, False, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x8354, 0x16, 23, False, "menu", "equip_attr.txt"),
        (0x8598, 0x0c,  9, False, "menu", "element.txt"),
        (0x8604, 0x24,  4, False, "menu", "remove.txt"),
        (0x8694, 0x1c, 42, False, "menu", "materia.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1cfc, 0x26,  6, False, "menu", "form1.txt"),
        (0x1de0, 0x16, 26, False, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x3250, 0x28, 25, False, "menu", "lv4_limit.txt"),
        (0x3d58, 0x12, 11, False, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x2120, 0x20, 14, False, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x293c, 0x16, 14, False, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e94, 0x0c, 10, False, "menu", "default_name.txt"),
        (0x8f0c, 0x0a,  8, False, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xef6c, 0x0a,  1, False, "menu", "save1.txt"),
        (0x12d90, 0x28, 37, False, "menu", "save2.txt"),
        (0x13372, 0x42, 20, False, "menu", "save3.txt"),
        (0x13910, 0x06,  1, False, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x4390, 0x28,  9, False, "menu", "shop_type.txt"),
        (0x44f8, 0x2e,  8, False, "menu", "shop_greeting1.txt"),
        (0x46c4, 0x2e,  8, False, "menu", "shop_greeting2.txt"),
        (0x62d0, 0x0c,  9, False, "menu", "element.txt"),
        (0x633c, 0x24,  4, False, "menu", "remove.txt"),
        (0x63cc, 0x1c, 42, False, "menu", "materia.txt"),
        (0x6868, 0x1e,  5, False, "menu", "shop_menu.txt"),
        (0x6900, 0x20, 10, False, "menu", "shop.txt"),
        (0x6a40, 0x16, 23, False, "menu", "equip_attr.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x1960, 0x0c,  9, False, "menu", "element.txt"),
        (0x19cc, 0x14, 27, False, "menu", "status.txt"),
        (0x1be8, 0x14, 27, False, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x53160, 0x08,  1, False, "battle", "pause.txt"),
        (0x5319c, 0x0e, 32, False, "battle", "status.txt"),
        (0x53390, 0x1c,  1, False, "battle", "gil1.txt"),
        (0x533ac, 0x04,  1, False, "battle", "gil2.txt"),
        (0x533b0, 0x08,  1, False, "battle", "gil3.txt"),
        (0x533b8, 0x14,  1, False, "battle", "gil4.txt"),
        (0x5350c, 0x08,  1, False, "battle", "arena1.txt"),
        (0x53514, 0x0c,  1, False, "battle", "arena2.txt"),
        (0x53520, 0x1a,  5, False, "battle", "arena3.txt"),
        (0x535a7, 0x1f, 24, False, "battle", "arena_handicap.txt"),
        (0x538b0, 0x23,  3, False, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x12b84, 0x06,  1, False, "chocobo", "black.txt"),
        (0x12ca8, 0x11, 24, False, "chocobo", "prices.txt"),
        (0x12e40, 0x08, 41, False, "chocobo", "names.txt"),
    ]),
]

# Spanish PAL version
execFileData_ES = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x398f8, 0x14, 23, False, "menu", "main.txt"),
        (0x39af8, 0x08,  3, True,  "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts use the 8x8 font with Japanese encoding
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1b3c, 0x46, 51, False, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x8354, 0x1a, 23, False, "menu", "equip_attr.txt"),
        (0x85e0, 0x0a,  9, False, "menu", "element.txt"),
        (0x863c, 0x28,  4, False, "menu", "remove.txt"),
        (0x86dc, 0x1e, 42, False, "menu", "materia.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1cf4, 0x28,  6, False, "menu", "form1.txt"),
        (0x1de4, 0x28, 26, False, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x3220, 0x28, 25, False, "menu", "lv4_limit.txt"),
        (0x3d28, 0x14, 11, False, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x2128, 0x28, 14, False, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x29cc, 0x28, 14, False, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e88, 0x0c, 10, False, "menu", "default_name.txt"),
        (0x8f00, 0x0c,  8, False, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xef6c, 0x08,  1, False, "menu", "save1.txt"),
        (0x12d8c, 0x24, 37, False, "menu", "save2.txt"),
        (0x13304, 0x44, 20, False, "menu", "save3.txt"),
        (0x138cc, 0x06,  1, False, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x4388, 0x28,  9, False, "menu", "shop_type.txt"),
        (0x44f0, 0x2e,  8, False, "menu", "shop_greeting1.txt"),
        (0x46bc, 0x2e,  8, False, "menu", "shop_greeting2.txt"),
        (0x62c8, 0x0a,  9, False, "menu", "element.txt"),
        (0x6324, 0x28,  4, False, "menu", "remove.txt"),
        (0x63c4, 0x1e, 42, False, "menu", "materia.txt"),
        (0x68b4, 0x1e,  5, False, "menu", "shop_menu.txt"),
        (0x694c, 0x1e, 10, False, "menu", "shop.txt"),
        (0x6a78, 0x14, 23, False, "menu", "equip_attr.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x1960, 0x0a,  9, False, "menu", "element.txt"),
        (0x19bc, 0x14, 26, False, "menu", "status.txt"),
        (0x1bc4, 0x1e, 27, False, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x53170, 0x08,  1, False, "battle", "pause.txt"),
        (0x531ac, 0x0c, 27, False, "battle", "status.txt"),
        (0x53324, 0x18,  1, False, "battle", "gil1.txt"),
        (0x5333c, 0x04,  1, False, "battle", "gil2.txt"),
        (0x53340, 0x08,  1, False, "battle", "gil3.txt"),
        (0x53348, 0x10,  1, False, "battle", "gil4.txt"),
        (0x53498, 0x08,  1, False, "battle", "arena1.txt"),
        (0x534a0, 0x20,  1, False, "battle", "arena2.txt"),
        (0x534c0, 0x1b,  5, False, "battle", "arena3.txt"),
        (0x53553, 0x27, 24, False, "battle", "arena_handicap.txt"),
        (0x5391c, 0x24,  3, False, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x12b84, 0x06,  1, False, "chocobo", "black.txt"),
        (0x12ca8, 0x11, 24, False, "chocobo", "prices.txt"),
        (0x12e40, 0x08, 41, False, "chocobo", "names.txt"),
    ]),
]

# US version
execFileData_US = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x39a48, 0x0c, 23, False, "menu", "main.txt"),
        (0x39b90, 0x08,  3, True,  "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts use the 8x8 font with Japanese encoding
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1ae8, 0x30, 51, False, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x82a4, 0x0c, 23, False, "menu", "equip_attr_short.txt"),
        (0x83f8, 0x0a,  9, False, "menu", "element.txt"),
        (0x8454, 0x24,  4, False, "menu", "remove.txt"),
        (0x84e4, 0x14,  6, False, "menu", "materia.txt"),
        (0x8570, 0x14, 35, False, "menu", "materia2.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1cfc, 0x26,  6, False, "menu", "form1.txt"),
        (0x1de0, 0x16, 26, False, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x3260, 0x22, 25, False, "menu", "lv4_limit.txt"),
        (0x3cd4, 0x0c, 11, False, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x2128, 0x24, 14, False, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x2934, 0x14, 14, False, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e6c, 0x0c, 10, False, "menu", "default_name.txt"),
        (0x8ee4, 0x08,  8, False, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xeedc, 0x08,  1, False, "menu", "save1.txt"),
        (0x12cfc, 0x24, 38, False, "menu", "save2.txt"),
        (0x13260, 0x30, 20, False, "menu", "save3.txt"),
        (0x13684, 0x06,  1, False, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x42c8, 0x14,  9, False, "menu", "shop_type.txt"),
        (0x437c, 0x2e,  8, False, "menu", "shop_greeting1.txt"),
        (0x4548, 0x2e,  8, False, "menu", "shop_greeting2.txt"),
        (0x6154, 0x0a,  9, False, "menu", "element.txt"),
        (0x61b0, 0x24,  4, False, "menu", "remove.txt"),
        (0x6240, 0x14,  6, False, "menu", "materia.txt"),
        (0x62cc, 0x14, 35, False, "menu", "materia2.txt"),
        (0x658c, 0x16, 23, False, "menu", "equip_attr.txt"),
        (0x678c, 0x14, 10, False, "menu", "shop.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x196c, 0x0a,  9, False, "menu", "element.txt"),
        (0x19c8, 0x14, 27, False, "menu", "status.txt"),
        (0x1be4, 0x0f, 27, False, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x53148, 0x08,  1, False, "battle", "pause.txt"),
        (0x53184, 0x0a, 32, False, "battle", "status.txt"),
        (0x532f8, 0x1c,  1, False, "battle", "gil1.txt"),
        (0x53314, 0x04,  1, False, "battle", "gil2.txt"),
        (0x53318, 0x08,  1, False, "battle", "gil3.txt"),
        (0x53320, 0x0c,  1, False, "battle", "gil4.txt"),
        (0x5346c, 0x0c,  1, False, "battle", "arena1.txt"),
        (0x53478, 0x18,  1, False, "battle", "arena2.txt"),
        (0x53490, 0x16,  5, False, "battle", "arena3.txt"),
        (0x53508, 0x20, 24, False, "battle", "arena_handicap.txt"),
        (0x53828, 0x22,  3, False, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x122c8, 0x06,  1, False, "chocobo", "black.txt"),
        (0x123ec, 0x10, 24, False, "chocobo", "prices.txt"),
        (0x1256c, 0x08, 44, False, "chocobo", "names.txt"),
    ]),
]

# Japanese International version
execFileData_JP = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x39880, 0x0c, 25, True, "menu", "main.txt"),
        (0x399e0, 0x08,  3, True, "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1a60, 0x1c, 51, True, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x81d0, 0x0e, 24, True, "menu", "equip_attr.txt"),
        (0x8354, 0x10,  4, True, "menu", "remove.txt"),
        (0x8394, 0x10, 42, True, "menu", "materia.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1c98, 0x14,  6, True, "menu", "form1.txt"),
        (0x1d10, 0x0f, 26, True, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x33d0, 0x28, 25, True, "menu", "lv4_limit.txt"),
        (0x3ed8, 0x08, 11, True, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x214c, 0x19, 14, True, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x28d0, 0x14, 14, True, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e34, 0x0c, 10, True, "menu", "default_name.txt"),
        (0x8eac, 0x08,  8, True, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xf070, 0x08,  1, True, "menu", "save1.txt"),
        (0x12e98, 0x22, 39, True, "menu", "save2.txt"),
        (0x133c2, 0x1e, 20, True, "menu", "save3.txt"),
        (0x13650, 0x20,  5, True, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x40d8, 0x14,  9, True, "menu", "shop_type.txt"),
        (0x418c, 0x14,  8, True, "menu", "shop_greeting1.txt"),
        (0x4254, 0x14,  8, True, "menu", "shop_greeting2.txt"),
        (0x431c, 0x14,  8, True, "menu", "shop_greeting3.txt"),
        (0x43e4, 0x14,  8, True, "menu", "shop_greeting4.txt"),
        (0x44ac, 0x14,  8, True, "menu", "shop_greeting5.txt"),
        (0x5fb4, 0x10,  4, True, "menu", "remove.txt"),
        (0x5ff4, 0x10, 42, True, "menu", "materia.txt"),
        (0x6298, 0x0e, 24, True, "menu", "equip_attr.txt"),
        (0x63f8, 0x10, 10, True, "menu", "shop.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x166c, 0x0a, 27, True, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x536d0, 0x08,  1, True, "battle", "pause.txt"),
        (0x5370c, 0x0c, 32, True, "battle", "status.txt"),
        (0x538b8, 0x18,  1, True, "battle", "gil1.txt"),
        (0x538d0, 0x04,  1, True, "battle", "gil2.txt"),
        (0x538d4, 0x08,  1, True, "battle", "gil3.txt"),
        (0x538dc, 0x08,  1, True, "battle", "gil4.txt"),
        (0x53a24, 0x10,  1, True, "battle", "arena1.txt"),
        (0x53a34, 0x10,  1, True, "battle", "arena2.txt"),
        (0x53a44, 0x10,  5, True, "battle", "arena3.txt"),
        (0x53a95, 0x11, 24, True, "battle", "arena_handicap.txt"),
        (0x53c50, 0x14,  3, True, "battle", "worried.txt"),
    ]),
    ("MINI", "CHOCOBO.BIN", [
        (0x12c80,  0x08,  1, True, "chocobo", "black.txt"),
        (0x12da0,  0x10, 24, True, "chocobo", "prices.txt"),
# TODO: In the Japanese version, each name has 6 characters, followed by 2 data bytes.
#       The translation tools cannot currently handle this.
#        (0x12f20, 0x108,  1, True, "chocobo", "names.txt"),
    ]),
]

# Original Japanese version
execFileData_JO = [

    # discDir, discFileName, offsetList
    ("", "<EXEC>", [
        # offset, stringSize, numStrings, jpEnc, transDir, transFileName
        (0x397f8, 0x0c, 25, True, "menu", "main.txt"),
        (0x39958, 0x08,  3, True, "menu", "main2.txt"),  # "HP"/"MP"/"LV" texts
    ]),
    ("MENU", "CNFGMENU.MNU", [
        (0x1a60, 0x1c, 51, True, "menu", "config.txt"),
    ]),
    ("MENU", "EQIPMENU.MNU", [
        (0x6310, 0x0e, 24, True, "menu", "equip_attr.txt"),
        (0x6494, 0x10,  4, True, "menu", "remove.txt"),
        (0x64d4, 0x10, 42, True, "menu", "materia.txt"),
    ]),
    ("MENU", "FORMMENU.MNU", [
        (0x1c98, 0x14,  6, True, "menu", "form1.txt"),
        (0x1d10, 0x0f, 26, True, "menu", "form2.txt"),
    ]),
    ("MENU", "ITEMMENU.MNU", [
        (0x33d0, 0x28, 25, True, "menu", "lv4_limit.txt"),
        (0x3ed8, 0x08, 11, True, "menu", "item.txt"),
    ]),
    ("MENU", "LIMTMENU.MNU", [
        (0x214c, 0x19, 14, True, "menu", "limit.txt"),
    ]),
    ("MENU", "MGICMENU.MNU", [
        (0x28d0, 0x14, 14, True, "menu", "magic.txt"),
    ]),
    ("MENU", "NAMEMENU.MNU", [
        (0x8e00, 0x10,  6, True, "menu", "name2.txt"),
        (0x8e60, 0x0c, 10, True, "menu", "default_name.txt"),
        (0x8ed8, 0x08,  8, True, "menu", "name.txt"),
    ]),
    ("MENU", "SAVEMENU.MNU", [
        ( 0xecf8, 0x08,  1, True, "menu", "save1.txt"),
        (0x13004, 0x18, 38, True, "menu", "save2.txt"),
        (0x1339a, 0x1e, 20, True, "menu", "save3.txt"),
        (0x13628, 0x20,  5, True, "menu", "save4.txt"),
    ]),
    ("MENU", "SHOPMENU.MNU", [
        (0x40d8, 0x14,  8, True, "menu", "shop_type.txt"),
        (0x4178, 0x14,  8, True, "menu", "shop_greeting1.txt"),
        (0x4240, 0x14,  8, True, "menu", "shop_greeting2.txt"),
        (0x4308, 0x14,  8, True, "menu", "shop_greeting3.txt"),
        (0x43d0, 0x14,  8, True, "menu", "shop_greeting4.txt"),
        (0x4498, 0x14,  8, True, "menu", "shop_greeting5.txt"),
        (0x5fa0, 0x10,  4, True, "menu", "remove.txt"),
        (0x5fe0, 0x10, 42, True, "menu", "materia.txt"),
        (0x6284, 0x0e, 24, True, "menu", "equip_attr.txt"),
        (0x63e4, 0x10, 10, True, "menu", "shop.txt"),
    ]),
    ("MENU", "STATMENU.MNU", [
        (0x166c, 0x0a, 27, True, "menu", "stat.txt"),
    ]),
    ("BATTLE", "BATTLE.X", [
        (0x536bc, 0x05, 32, True, "battle", "status.txt"),
        (0x53788, 0x18,  1, True, "battle", "gil1.txt"),
        (0x537a0, 0x04,  1, True, "battle", "gil2.txt"),
        (0x537a4, 0x08,  1, True, "battle", "gil3.txt"),
        (0x537ac, 0x08,  1, True, "battle", "gil4.txt"),
        (0x538f4, 0x10,  1, True, "battle", "arena1.txt"),
        (0x53904, 0x10,  1, True, "battle", "arena2.txt"),
        (0x53914, 0x10,  5, True, "battle", "arena3.txt"),
        (0x53965, 0x11, 24, True, "battle", "arena_handicap.txt"),
        (0x53b20, 0x14,  3, True, "battle", "worried.txt"),
    ]),
    ("FIELD", "CHOCOBO.BIN", [
        (0x12318,  0x08,  1, True, "chocobo", "black.txt"),
        (0x12438,  0x10, 24, True, "chocobo", "prices.txt"),
# TODO: In the Japanese version, each name has 6 characters, followed by 2 data bytes.
#       The translation tools cannot currently handle this.
#        (0x125b0, 0x108,  1, True, "chocobo", "names.txt"),
    ]),
]

def execFileData(version):
    if version == ff7.Version.EN:
        return execFileData_EN
    elif version == ff7.Version.FR:
        return execFileData_FR
    elif version == ff7.Version.DE:
        return execFileData_DE
    elif version == ff7.Version.ES:
        return execFileData_ES
    elif version == ff7.Version.US:
        return execFileData_US
    elif version == ff7.Version.JP:
        return execFileData_JP
    elif version == ff7.Version.JO:
        return execFileData_JO
    else:
        return []


#
# Translatable strings embedded in snowboard minigame (SNOBO2)
#

# English and Japanese International versions
snobo2Data_EN = [
    # offset, stringSize
    (0x354, 8),
    (0x35c, 12),
    (0x368, 8),
    (0x370, 12),
    (0x37c, 8),
    (0x384, 8),
    (0x38c, 8),
    (0x394, 8),
    (0x39c, 4),
    (0x3a0, 8),
    (0x3a8, 8),
    (0x3b0, 8),
    (0x3b8, 8),
    (0x3c0, 4),
    (0x3c4, 8),
    (0x3cc, 8),
    (0x3d4, 8),
    (0x3dc, 8),
    (0x3e4, 12),
    (0x3f0, 8),
    (0x3f8, 8),
    (0x400, 8),
    (0x408, 8),
    (0x410, 8),
    (0x418, 8),
    (0x420, 8),
    (0x428, 8),
    (0x430, 8),
    (0x438, 8),
    (0x440, 5),
]

# French European version
snobo2Data_FR = [
    # offset, stringSize
    (0x350, 12),
    (0x35c, 8),
    (0x364, 12),
    (0x370, 12),
    (0x37c, 8),
    (0x384, 8),
    (0x38c, 12),
    (0x398, 8),
    (0x3a0, 12),
    (0x3ac, 8),
    (0x3b4, 8),
    (0x3bc, 8),
    (0x3c4, 12),
    (0x3d0, 4),
    (0x3d4, 8),
    (0x3dc, 8),
    (0x3e4, 8),
    (0x3ec, 12),
    (0x3f8, 8),
    (0x400, 8),
    (0x408, 8),
    (0x410, 8),
    (0x418, 8),
    (0x420, 8),
    (0x428, 8),
    (0x430, 8),
    (0x438, 8),
    (0x440, 8),
    (0x448, 6),
]

# German European version
snobo2Data_DE = [
    # offset, stringSize
    (0x350, 8),
    (0x358, 16),
    (0x368, 8),
    (0x370, 8),
    (0x378, 12),
    (0x384, 8),
    (0x38c, 8),
    (0x394, 12),
    (0x3a0, 8),
    (0x3a8, 4),
    (0x3ac, 8),
    (0x3b4, 8),
    (0x3bc, 12),
    (0x3c8, 8),
    (0x3d0, 4),
    (0x3d4, 8),
    (0x3dc, 8),
    (0x3e4, 8),
    (0x3ec, 8),
    (0x3f4, 8),
    (0x3fc, 8),
    (0x404, 8),
    (0x40c, 8),
    (0x414, 8),
    (0x41c, 8),
    (0x424, 4),
    (0x428, 4),
    (0x42c, 4),
    (0x430, 4),
    (0x434, 3),
]

# Spanish European version
snobo2Data_ES = [
    # offset, stringSize
    (0x350, 8),
    (0x358, 8),
    (0x360, 12),
    (0x36c, 12),
    (0x378, 8),
    (0x380, 8),
    (0x388, 8),
    (0x390, 4),
    (0x394, 8),
    (0x39c, 8),
    (0x3a4, 8),
    (0x3ac, 12),
    (0x3b8, 12),
    (0x3c4, 4),
    (0x3c8, 8),
    (0x3d0, 8),
    (0x3d8, 8),
    (0x3e0, 12),
    (0x3ec, 8),
    (0x3f4, 8),
    (0x3fc, 8),
    (0x404, 8),
    (0x40c, 8),
    (0x414, 8),
    (0x41c, 8),
    (0x424, 8),
    (0x42c, 8),
    (0x434, 8),
    (0x43c, 8),
]

def snobo2Data(version):
    if version in [ff7.Version.EN, ff7.Version.US, ff7.Version.JP]:
        return snobo2Data_EN
    elif version == ff7.Version.FR:
        return snobo2Data_FR
    elif version == ff7.Version.DE:
        return snobo2Data_DE
    elif version == ff7.Version.ES:
        return snobo2Data_ES
    else:
        return None


#
# World module string list offset and size
#

def worldStringListOffset(version):
    if version == ff7.Version.EN:
        return 0x1e5b4  # English European version
    elif version == ff7.Version.FR:
        return 0x1e5b4  # French European version
    elif version == ff7.Version.DE:
        return 0x1e5b4  # German European version
    elif version == ff7.Version.ES:
        return 0x1e5b4  # Spanish European version
    elif version == ff7.Version.US:
        return 0x1e5f0  # US verson
    elif version == ff7.Version.JP:
        return 0x1e5c0  # Japanese International version
    elif version == ff7.Version.JO:
        return 0x1e430  # Original Japanese version
    else:
        return None

worldStringListSize = 0x1000


#
# Offset of sorting table in ITEMMENU.MNU
#

def itemTableOffset(version):
    if version == ff7.Version.EN:
        return 0x35b4  # English European version
    elif version == ff7.Version.FR:
        return 0x3838  # French European version
    elif version == ff7.Version.DE:
        return 0x3638  # German European version
    elif version == ff7.Version.ES:
        return 0x3608  # Spanish European version
    elif version == ff7.Version.US:
        return 0x35b4  # US version
    elif version == ff7.Version.JP:
        return 0x37b8  # Japanese version
    else:
        return None


#
# List of field maps, excluding the following ones which are dummied out or
# contain no text in any version of the game:
# - BLACKBGD
# - BLACKBGF
# - BLACKBGG
# - BLIN69_2
# - CONVIL_3
# - DUMMY
# - FSHIP_26
# - HYOU14
# - JUNMON
# - LAS4_42
# - M_ENDO
# - NIVGATE3
# - NIVINN_3
# - NIVL_4
# - PASS
# - Q_5
# - SUBIN_4
# - TRAP
# - WM*
# - XMVTES
#

mapNames = [
    "4SBWY_1", "4SBWY_22", "4SBWY_2", "4SBWY_3", "4SBWY_4", "4SBWY_5",
    "4SBWY_6", "5MIN1_1", "5MIN1_2", "5TOWER", "7MIN1", "ANCNT1", "ANCNT2",
    "ANCNT3", "ANCNT4", "ANFRST_1", "ANFRST_2", "ANFRST_3", "ANFRST_4",
    "ANFRST_5", "ASTAGE_A", "ASTAGE_B", "BIGWHEEL", "BLACKBG1", "BLACKBG2",
    "BLACKBG3", "BLACKBG4", "BLACKBG5", "BLACKBG6", "BLACKBG7", "BLACKBG8",
    "BLACKBG9", "BLACKBGA", "BLACKBGB", "BLACKBGC", "BLACKBGE", "BLACKBGH",
    "BLACKBGI", "BLACKBGJ", "BLACKBGK", "BLIN1", "BLIN2", "BLIN2_I",
    "BLIN3_1", "BLIN59", "BLIN60_1", "BLIN60_2", "BLIN61", "BLIN62_1",
    "BLIN62_2", "BLIN62_3", "BLIN63_1", "BLIN63_T", "BLIN64", "BLIN65_1",
    "BLIN65_2", "BLIN66_1", "BLIN66_2", "BLIN66_3", "BLIN66_4", "BLIN66_5",
    "BLIN66_6", "BLIN671B", "BLIN67_1", "BLIN67_2", "BLIN673B", "BLIN67_3",
    "BLIN67_4", "BLIN68_1", "BLIN68_2", "BLIN69_1", "BLIN70_1", "BLIN70_2",
    "BLIN70_3", "BLIN70_4", "BLINELE", "BLINST_1", "BLINST_2", "BLINST_3",
    "BLUE_1", "BLUE_2", "BONEVIL2", "BONEVIL", "BUGIN1A", "BUGIN1B",
    "BUGIN1C", "BUGIN2", "BUGIN3", "BWHLIN2", "BWHLIN", "CANON_1",
    "CANON_2", "CARGOIN", "CHORACE2", "CHORACE", "CHRIN_1A", "CHRIN_1B",
    "CHRIN_2", "CHRIN_3A", "CHRIN_3B", "CHURCH", "CLSIN2_1", "CLSIN2_2",
    "CLSIN2_3", "COLNE_1", "COLNE_2", "COLNE_3", "COLNE_4", "COLNE_5",
    "COLNE_6", "COLNE_B1", "COLNE_B3", "COLOIN1", "COLOIN2", "COLOSS",
    "CONDOR1", "CONDOR2", "CONVIL_1", "CONVIL_2", "CONVIL_4", "COREL1",
    "COREL2", "COREL3", "CORELIN", "COS_BTM2", "COS_BTM", "COSIN1_1",
    "COSIN1", "COSIN2", "COSIN3", "COSIN4", "COSIN5", "COSMIN2", "COSMIN3",
    "COSMIN4", "COSMIN6", "COSMIN7", "COSMO2", "COSMO", "COS_TOP",
    "CRATER_1", "CRATER_2", "CRCIN_1", "CRCIN_2", "DATIAO_1", "DATIAO_2",
    "DATIAO_3", "DATIAO_4", "DATIAO_5", "DATIAO_6", "DATIAO_7", "DATIAO_8",
    "DEL12", "DEL1", "DEL2", "DEL3", "DELINN", "DELMIN12", "DELMIN1",
    "DELMIN2", "DELPB", "DESERT1", "DESERT2", "DYNE", "EALIN_12", "EALIN_1",
    "EALIN_2", "EALS_1", "ELEOUT", "ELEVTR1", "ELM", "ELM_I", "ELMIN1_1",
    "ELMIN1_2", "ELMIN2_1", "ELMIN2_2", "ELMIN3_1", "ELMIN3_2", "ELMIN4_1",
    "ELMIN4_2", "ELMINN_1", "ELMINN_2", "ELMPB", "ELMTOW", "ELM_WA",
    "FALLP", "FARM", "FRCYO2", "FRCYO", "FR_E", "FRMIN", "FSHIP_12",
    "FSHIP_1", "FSHIP_22", "FSHIP_23", "FSHIP_24", "FSHIP_25", "FSHIP_2",
    "FSHIP_3", "FSHIP_42", "FSHIP_4", "FSHIP_5", "GAIA_1", "GAIA_2",
    "GAIA_31", "GAIA_32", "GAIAFOOT", "GAIIN_1", "GAIIN_2", "GAIIN_3",
    "GAIIN_4", "GAIIN_5", "GAIIN_6", "GAIIN_7", "GAMES_1", "GAMES_2",
    "GAMES", "GHOTEL", "GHOTIN_1", "GHOTIN_2", "GHOTIN_3", "GHOTIN_4",
    "GIDUN_1", "GIDUN_2", "GIDUN_3", "GIDUN_4", "GLDELEV", "GLDGATE",
    "GLDINFO", "GLDST", "GNINN", "GNMK", "GNMKF", "GOMIN", "GONGAGA",
    "GON_I", "GONJUN1", "GONJUN2", "GON_WA1", "GON_WA2", "GOSON", "HEKIGA",
    "HIDEWAY1", "HIDEWAY2", "HIDEWAY3", "HILL2", "HILL", "HOLU_1", "HOLU_2",
    "HYOU10", "HYOU11", "HYOU12", "HYOU13_1", "HYOU13_2", "HYOU1", "HYOU2",
    "HYOU3", "HYOU4", "HYOU5_1", "HYOU5_2", "HYOU5_3", "HYOU5_4", "HYOU6",
    "HYOU7", "HYOU8_1", "HYOU8_2", "HYOU9", "HYOUMAP", "ICEDUN_1",
    "ICEDUN_2", "ITHILL", "ITHOS", "ITMIN1", "ITMIN2", "ITOWN12", "ITOWN1A",
    "ITOWN1B", "ITOWN2", "ITOWN_I", "ITOWN_M", "ITOWN_W", "JAIL1", "JAIL2",
    "JAIL3", "JAIL4", "JAILIN1", "JAILIN2", "JAILIN3", "JAILIN4", "JAILPB",
    "JET", "JETIN1", "JTEMPLB", "JTEMPLC", "JTEMPL", "JTMPIN1", "JTMPIN2",
    "JUMIN", "JUN_A", "JUNAIR2", "JUNAIR", "JUNBIN12", "JUNBIN1",
    "JUNBIN21", "JUNBIN22", "JUNBIN3", "JUNBIN4", "JUNBIN5", "JUNDOC1A",
    "JUNDOC1B", "JUNELE1", "JUNELE2", "JUN_I1", "JUN_I2", "JUNIN1A",
    "JUNIN1", "JUNIN2", "JUNIN3", "JUNIN4", "JUNIN5", "JUNIN6", "JUNIN7",
    "JUNINN", "JUN_M", "JUNMIN1", "JUNMIN2", "JUNMIN3", "JUNMIN4",
    "JUNMIN5", "JUNON", "JUNONE22", "JUNONE2", "JUNONE3", "JUNONE4",
    "JUNONE5", "JUNONE6", "JUNONE7", "JUNONL1", "JUNONL2", "JUNONL3",
    "JUNONR1", "JUNONR2", "JUNONR3", "JUNONR4", "JUNPB_1", "JUNPB_2",
    "JUNPB_3", "JUNSBD1", "JUN_WA", "JUN_W", "KURO_10", "KURO_11",
    "KURO_12", "KURO_1", "KURO_2", "KURO_3", "KURO_4", "KURO_5", "KURO_6",
    "KURO_7", "KURO_82", "KURO_8", "KURO_9", "LAS0_1", "LAS0_2", "LAS0_3",
    "LAS0_4", "LAS0_5", "LAS0_6", "LAS0_7", "LAS0_8", "LAS1_1", "LAS1_2",
    "LAS1_3", "LAS1_4", "LAS2_1", "LAS2_2", "LAS2_3", "LAS2_4", "LAS3_1",
    "LAS3_2", "LAS3_3", "LAS4_0", "LAS4_1", "LAS4_2", "LAS4_3", "LAS4_4",
    "LASTMAP", "LIFE2", "LIFE", "LOSIN1", "LOSIN2", "LOSIN3", "LOSINN",
    "LOSLAKE1", "LOSLAKE2", "LOSLAKE3", "LOST1", "LOST2", "LOST3", "MD0",
    "MD1_1", "MD1_2", "MD1STIN", "MD8_1", "MD8_2", "MD8_32", "MD8_3",
    "MD8_4", "MD8_52", "MD8_5", "MD8_6", "MD8_B1", "MD8_B2", "MD8BRDG2",
    "MD8BRDG", "MD_E1", "MDS5_1", "MDS5_2", "MDS5_3", "MDS5_4", "MDS5_5",
    "MDS5_DK", "MDS5_I", "MDS5_M", "MDS5_W", "MDS6_1", "MDS6_22", "MDS6_2",
    "MDS6_3", "MDS7", "MDS7_IM", "MDS7PB_1", "MDS7PB_2", "MDS7PLR1",
    "MDS7PLR2", "MDS7ST1", "MDS7ST2", "MDS7ST32", "MDS7ST33", "MDS7ST3",
    "MDS7_W1", "MDS7_W2", "MDS7_W3", "MIDGAL", "MKT_IA", "MKTINN", "MKT_M",
    "MKT_MENS", "MKTPB", "MKT_S1", "MKT_S2", "MKT_S3", "MKT_W", "MOGU_1",
    "MOVE_D", "MOVE_F", "MOVE_I", "MOVE_R", "MOVE_S", "MOVE_U", "MRKT1",
    "MRKT2", "MRKT3", "MRKT4", "MTCRL_0", "MTCRL_1", "MTCRL_2", "MTCRL_3",
    "MTCRL_4", "MTCRL_5", "MTCRL_6", "MTCRL_7", "MTCRL_8", "MTCRL_9",
    "MTNVL2", "MTNVL3", "MTNVL4", "MTNVL5", "MTNVL6B", "MTNVL6", "NCOIN1",
    "NCOIN2", "NCOIN3", "NCOINN", "NCOREL2", "NCOREL3", "NCOREL", "NIV_CL",
    "NIVGATE2", "NIVGATE4", "NIVGATE", "NIVINN_1", "NIVINN_2", "NIVL_2",
    "NIVL_3", "NIVL_B12", "NIVL_B1", "NIVL_B22", "NIVL_B2", "NIVL",
    "NIVL_E1", "NIVL_E2", "NIVL_E3", "NIV_TI1", "NIV_TI2", "NIV_TI3",
    "NIV_TI4", "NIV_W", "NMKIN_1", "NMKIN_2", "NMKIN_3", "NMKIN_4",
    "NMKIN_5", "NRTHMK", "NVDUN1", "NVDUN2", "NVDUN31", "NVDUN3", "NVDUN4",
    "NVMIN1_1", "NVMIN1_2", "NVMKIN1", "NVMKIN21", "NVMKIN22", "NVMKIN23",
    "NVMKIN31", "NVMKIN32", "ONNA_1", "ONNA_2", "ONNA_3", "ONNA_4",
    "ONNA_52", "ONNA_5", "ONNA_6", "PILLAR_1", "PILLAR_2", "PILLAR_3",
    "PRISILA", "PSDUN_1", "PSDUN_2", "PSDUN_3", "PSDUN_4", "Q_1", "Q_2",
    "Q_3", "Q_4", "RCKT2", "RCKT32", "RCKT3", "RCKTBAS1", "RCKTBAS2",
    "RCKT", "RCKTIN1", "RCKTIN2", "RCKTIN3", "RCKTIN4", "RCKTIN5",
    "RCKTIN6", "RCKTIN7", "RCKTIN8", "RKT_I", "RKTINN1", "RKTINN2",
    "RKTMIN1", "RKTMIN2", "RKTSID", "RKT_W", "ROADEND", "ROOTMAP", "ROPEST",
    "SANDUN_1", "SANDUN_2", "SANGO1", "SANGO2", "SANGO3", "SEA", "SEMKIN_1",
    "SEMKIN_2", "SEMKIN_3", "SEMKIN_4", "SEMKIN_5", "SEMKIN_6", "SEMKIN_7",
    "SEMKIN_8", "SETO1", "SHIP_1", "SHIP_2", "SHPIN_22", "SHPIN_2",
    "SHPIN_3", "SICHI", "SINBIL_1", "SINBIL_2", "SININ1_1", "SININ1_2",
    "SININ2_1", "SININ2_2", "SININ3", "SININB1", "SININB2", "SININB31",
    "SININB32", "SININB33", "SININB34", "SININB35", "SININB36", "SININB41",
    "SININB42", "SININB51", "SININB52", "SKY", "SLFRST_1", "SLFRST_2",
    "SMKIN_1", "SMKIN_2", "SMKIN_3", "SMKIN_4", "SMKIN_5", "SNINN_1",
    "SNINN_2", "SNINN_B1", "SNMAYOR", "SNMIN1", "SNMIN2", "SNOW", "SNW_W",
    "SOUTHMK1", "SOUTHMK2", "SPGATE", "SPIPE_1", "SPIPE_2", "STARTMAP",
    "SUBIN_1A", "SUBIN_1B", "SUBIN_2A", "SUBIN_2B", "SUBIN_3", "TIN_1",
    "TIN_2", "TIN_3", "TIN_4", "TRACKIN2", "TRACKIN", "TRNAD_1", "TRNAD_2",
    "TRNAD_3", "TRNAD_4", "TRNAD_51", "TRNAD_52", "TRNAD_53", "TUNNEL_1",
    "TUNNEL_2", "TUNNEL_3", "TUNNEL_4", "TUNNEL_5", "TUNNEL_6", "UJUNON1",
    "UJUNON2", "UJUNON3", "UJUNON4", "UJUNON5", "UJUN_W", "UTA_IM", "UTAPB",
    "UTA_WA", "UTMIN1", "UTMIN2", "UTTMPIN1", "UTTMPIN2", "UTTMPIN3",
    "UTTMPIN4", "UUTAI1", "UUTAI2", "WCRIMB_1", "WCRIMB_2", "WHITE1",
    "WHITE2", "WHITEBG1", "WHITEBG2", "WHITEBG3", "WHITEIN", "WOA_1",
    "WOA_2", "WOA_3", "YOUGAN2", "YOUGAN3", "YOUGAN", "YUFY1", "YUFY2",
    "ZCOAL_1", "ZCOAL_2", "ZCOAL_3", "ZMIND1", "ZMIND2", "ZMIND3", "ZTRUCK",
    "ZZ1", "ZZ2", "ZZ3", "ZZ4", "ZZ5", "ZZ6", "ZZ7", "ZZ8",
]

def fieldMaps(version):
    maps = mapNames

    # The FRCYO2 map (Chocobo stable disc 2/3) is only present in European
    # versions of the game.
    if not ff7.isEuropean(version):
        maps.remove("FRCYO2")

    # Some maps from the original Japanese release were dummied out in later
    # versions, others were added
    if version == ff7.Version.JO:
        maps.remove("MDS7ST33")
        maps.remove("MIDGAL")
        maps.remove("NIVGATE4")
        maps.remove("SININB34")
        maps.remove("SININB35")
        maps.remove("SININB36")
        maps.remove("ZTRUCK")
    else:
        maps.remove("BLACKBGA")
        maps.remove("FALLP")
        maps.remove("ONNA_1")
        maps.remove("ONNA_3")
        maps.remove("ONNA_6")
        maps.remove("WHITEBG1")
        maps.remove("WHITEBG2")

    return maps
