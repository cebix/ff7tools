# -*- coding: utf-8 -*-

#
# ff7.ff7text - Final Fantasy VII text manipulation
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import re
import struct


# Characters in range 0x00..0xdf directly map to Unicode characters.
# This is almost identical to the MacOS Roman encoding shifted down
# by 32 positions.
normalChars = (
    " !\"#$%&'()*+,-./01234"
    "56789:;<=>?@ABCDEFGHI"
    "JKLMNOPQRSTUVWXYZ[\\]^"
    "_`abcdefghijklmnopqrs"
    "tuvwxyz{|}~ ÄÅÇÉÑÖÜáà"
    "âäãåçéèêëíìîïñóòôöõúù"
    "ûü♥°¢£↔→♪ßα  ´¨≠ÆØ∞±≤"  # '♥' (0x80), '↔' (0x84), '→' (0x85), '♪' (0x86), and 'α' (0x88) are additions
    "≥¥µ∂ΣΠπ⌡ªºΩæø¿¡¬√ƒ≈∆«"
    "»… ÀÃÕŒœ–—“”‘’÷◊ÿŸ⁄ ‹"
    "›ﬁﬂ■‧‚„‰ÂÊÁËÈÍÎÏÌÓÔ Ò"
    "ÚÛÙıˆ˜¯˘˙˚¸˝˛ˇ       "
)

# Japanese font texture 1, CLUT 0, upper half
normalCharsJP = (
    "バばビびブぶベべボぼガがギぎグぐゲげゴごザ"
    "ざジじズずゼぜゾぞダだヂぢヅづデでドどヴパ"
    "ぱピぴプぷペぺポぽ0123456789、。"
    " ハはヒひフふヘへホほカかキきクくケけコこ"
    "サさシしスすセせソそタたチちツつテてトとウ"
    "うアあイいエえオおナなニにヌぬネねノのマま"
    "ミみムむメめモもラらリりルるレれロろヤやユ"
    "ゆヨよワわンんヲをッっャゃュゅョょァぁィぃ"
    "ゥぅェぇォぉ!?『』．+ABCDEFGHI"
    "JKLMNOPQRSTUVWXYZ・*ー〜"
    "…%/:&【】♥→αβ「」()-=   ⑬"
)

# Japanese font texture 1, CLUT 0, lower half
kanjiSet1 = (
    "必殺技地獄火炎裁雷大怒斬鉄剣槍海衝聖審判転"
    "生改暗黒釜天崩壊零式自爆使放射臭息死宣告凶"
    "破晄撃画龍晴点睛超究武神覇癒風邪気封印吹烙"
    "星守護命鼓動福音掌打水面蹴乱闘合体疾迅明鏡"
    "止抜山蓋世血祭鎧袖一触者滅森羅万象装備器攻"
    "魔法召喚獣呼出持相手物確率弱投付与変化片方"
    "行決定分直前真似覚列後位置防御発回連続敵全"
    "即効果尾毒消金針乙女興奮剤鎮静能薬英雄榴弾"
    "右腕砂時計糸戦惑草牙南極冷結晶電鳥角有害質"
    "爪光月反巨目砲重力球空双野菜実兵単毛茶色髪"
)

# Japanese font texture 1, CLUT 1, upper half
kanjiSet2 = (
    "安香花会員蜂蜜館下着入先不子供屋商品景交換"
    "階模型部離場所仲間無制限殿様秘氷河図何材料"
    "雪上進事古代種鍵娘紙町住奥眠楽最初村雨釘陸"
    "吉揮叢雲軍異常通威父蛇矛青偃刀戟十字裏車円"
    "輪卍折鶴倶戴螺貝突銀玉正宗具甲烈属性吸収半"
    "減土高級状態縁闇睡石徐々的指混呪開始歩復盗"
    "小治理同速遅逃去視複味沈黙還倍数瀕取返人今"
    "差誰当拡散飛以外暴避振身中旋津波育機械擲炉"
    "新両本君洞内作警特殊板強穴隊族亡霊鎖足刃頭"
    "怪奇虫跳侍左首潜長親衛塔宝条像忍謎般見報充"
    "填完了銃元経験値終獲得名悲蛙操成費背切替割"
)

# Japanese font texture 1, CLUT 1, lower half
kanjiSet3 = (
    "由閉記憶選番街底忘都過艇路運搬船基心港末宿"
    "西道艦家乗竜巻迷宮絶壁支社久件想秒予多落受"
    "組余系標起迫日勝形引現解除磁互口廃棄汚染液"
    "活令副隠主斉登温泉百段熱走急降奪響嵐移危戻"
    "遠吠軟骨言葉震叫噴舞狩粉失敗眼激盤逆鱗踏喰"
    "盾叩食凍退木吐線魅押潰曲翼教皇太陽界案挑援"
    "赤往殴意東北参知聞来仕別集信用思毎悪枯考然"
    "張好伍早各独配腐話帰永救感故売浮市加流約宇"
    "礼束母男年待宙立残俺少精士私険関倒休我許郷"
    "助要問係旧固荒稼良議導夢追説声任柱満未顔旅"
)

# Japanese font texture 2, CLUT 0
kanjiSet4 = (
    "友伝夜探対調民読占頼若学識業歳争苦織困答準"
    "恐認客務居他再幸役縮情豊夫近窟責建求迎貸期"
    "工算湿難保帯届凝笑向可遊襲申次国素題普密望"
    "官泣創術演輝買途浴老幼利門格原管牧炭彼房驚"
    "禁注整衆語証深層査渡号科欲店括坑酬緊研権書"
    "暇兄派造広川賛駅絡在党岸服捜姉敷胸刑谷痛岩"
    "至勢畑姿統略抹展示修酸製歓接障災室索扉傷録"
    "優基讐勇司境璧医怖狙協犯資設雇根億脱富躍純"
    "写病依到練順園総念維検朽圧補公働因朝浪祝恋"
    "郎勉春功耳恵緑美辺昇悩泊低酒影競二矢瞬希志"
)

# Japanese font texture 2, CLUT 1
kanjiSet5 = (
    "孫継団給抗違提断島栄油就僕存企比浸非応細承"
    "編排努締談趣埋営文夏個益損額区寒簡遣例肉博"
    "幻量昔臓負討悔膨飲妄越憎増枚皆愚療庫涙照冗"
    "壇坂訳抱薄義騒奴丈捕被概招劣較析繁殖耐論貴"
    "称千歴史募容噂壱胞鳴表雑職妹氏踊停罪甘健焼"
    "払侵頃愛便田舎孤晩清際領評課勤謝才偉誤価欠"
    "寄忙従五送周頑労植施販台度嫌諸習緒誘仮借輩"
    "席戒弟珍酔試騎霜鉱裕票券専祖惰偶怠罰熟牲燃"
    "犠快劇拠厄抵適程繰腹橋白処匹杯暑坊週秀看軽"
    "棊和平王姫庭観航横帳丘亭財律布規謀積刻陥類"
)

def decodeKanji(bank, code):
    if bank == 0xfa:
        return kanjiSet1[code]
    elif bank == 0xfb:
        return kanjiSet2[code]
    elif bank == 0xfc:
        return kanjiSet3[code]
    elif bank == 0xfd:
        return kanjiSet4[code]
    elif bank == 0xfe:
        return kanjiSet5[code]

    raise IndexError("Invalid kanji bank %02x" % bank)


# Special characters of the field module (0xe0..0xff)
fieldSpecialChars = {

    # Not in Japanese version, where 0xe0..0xe6 are regular characters:
    0xe0: "{CHOICE}",    # choice tab (10 spaces)
    0xe1: "\t",          # tab (4 spaces)
    0xe2: ", ",          # shortcut
    0xe3: '."',          # not very useful shortcut with the wrong quote character...
    0xe4: '…"',          # not very useful shortcut with the wrong quote character...

    # In all versions
    0xe6: "⑬",           # appears in the US version of BLACKBG6, presumably a mistake
    0xe7: "\n",          # new line
    0xe8: "{NEW}",       # new page

    0xea: "{CLOUD}",
    0xeb: "{BARRET}",
    0xec: "{TIFA}",
    0xed: "{AERITH}",
    0xee: "{RED XIII}",
    0xef: "{YUFFIE}",
    0xf0: "{CAIT SITH}",
    0xf1: "{VINCENT}",
    0xf2: "{CID}",
    0xf3: "{PARTY #1}",
    0xf4: "{PARTY #2}",
    0xf5: "{PARTY #3}",

    0xf6: "〇",          # controller button
    0xf7: "△",           # controller button
    0xf8: "☐",           # controller button
    0xf9: "✕",           # controller button

    0xfa: "",            # kanji 1
    0xfb: "",            # kanji 2
    0xfc: "",            # kanji 3
    0xfd: "",            # kanji 4

    # 0xfe                # extended control code, see below
    # 0xff                # end of string
}

# Extended control codes of the field module (0xfe ..)
fieldControlCodes = {
    0xd2: "{GRAY}",
    0xd3: "{BLUE}",
    0xd4: "{RED}",
    0xd5: "{PURPLE}",
    0xd6: "{GREEN}",
    0xd7: "{CYAN}",
    0xd8: "{YELLOW}",
    0xd9: "{WHITE}",
    0xda: "{FLASH}",
    0xdb: "{RAINBOW}",

    0xdc: "{PAUSE}",   # pause until OK button is pressed
    # 0xdd              # wait # of frames
    0xde: "{NUM}",     # decimal variable
    0xdf: "{HEX}",     # hex variable
    0xe0: "{SCROLL}",  # wait for OK butten, then scroll window
    0xe1: "{RNUM}",    # decimal variable, right-aligned
    # 0xe2              # value from game state memory
    0xe9: "{FIXED}",   # fixed-width character spacing on/off
}

# Inverse mapping of field module commands to codes
fieldCommands = {v:bytes([k]) for k, v in fieldSpecialChars.items() if v}
fieldCommands.update({v:bytes([0xfe, k]) for k, v in fieldControlCodes.items()})

# Characters which must be escaped when decoding
escapeChars = "\\{}"


# Decode FF7 field text string to unicode string.
def decodeField(data, japanese = False):
    if japanese:
        charset = normalCharsJP
        numNormalChars = 0xe7
    else:
        charset = normalChars
        numNormalChars = 0xe0

    dataSize = len(data)
    text = ""

    i = 0
    while i < dataSize:
        c = data[i]
        i += 1

        if c == 0xff:

            # End of string
            break

        elif c < numNormalChars:

            # Regular printable character
            t = charset[c]

            if t in escapeChars:
                text += "\\"

            text += t

        elif c >= 0xfa and c <= 0xfd and japanese:

            # Kanji
            if i >= dataSize:
                raise IndexError("Spurious kanji code %02x at end of string %r" % (c, data))

            k = data[i]
            i += 1

            text += decodeKanji(c, k)

        elif c == 0xfe:

            # Field module control code or kanji
            if i >= dataSize:
                raise IndexError("Spurious control code %02x at end of string %r" % (c, data))

            k = data[i]
            i += 1

            if k < 0xd2 and japanese:

                text += decodeKanji(c, k)

            elif k == 0xdd:

                # WAIT <arg> command
                if i >= dataSize - 1:
                    raise IndexError("Spurious WAIT command at end of string %r" % data)

                arg = struct.unpack_from("<H", data, i)
                i += 2

                text += "{WAIT %d}" % arg

            elif k == 0xe2:

                # STR <offset> <length> command
                if i >= dataSize - 3:
                    raise IndexError("Spurious STR command at end of string %r" % data)

                offset, length = struct.unpack_from("<HH", data, i)
                i += 4

                text += "{STR %04x %04x}" % (offset, length)

            else:

                # Other control code
                if not k in fieldControlCodes:
                    raise IndexError("Illegal control code %02x in field string %r" % (k, data))

                text += fieldControlCodes[k]
                
        else:

            # Field module special character
            t = fieldSpecialChars[c]

            if not t:
                raise IndexError("Illegal character %02x in field string %r" % (c, data))

            if c == 0xe8:  # newline after {NEW}
                t += '\n'

            text += t

    return text


# Control codes referencing kernel variables
kernelVars = {
    0xea: "CHAR",
    0xeb: "ITEM",
    0xec: "NUM",
    0xed: "TARGET",
    0xee: "ATTACK",
    0xef: "ID",
    0xf0: "ELEMENT",
}


# Decode FF7 kernel text string to unicode string.
def decodeKernel(data, japanese = False):
    if japanese:
        charset = normalCharsJP
    else:
        charset = normalChars

    dataSize = len(data)
    text = ""

    i = 0
    while i < dataSize:
        c = data[i]
        i += 1

        if c == 0xff:

            # End of string
            break

        elif c < 0xe7:

            # Regular printable character
            t = charset[c]

            if t in escapeChars:
                text += "\\"

            text += t

        elif c >= 0xea and c <= 0xf0:

            # Kernel variable
            if i >= dataSize - 1:
                raise IndexError("Spurious control code %02x at end of kernel string %r" % (c, data))

            text += "{%s %02x %02x}" % (kernelVars[c], data[i], data[i+1])
            i += 2

        elif c == 0xf8:

            # Text box color
            if i >= dataSize:
                raise IndexError("Spurious color code at end of kernel string %r" % data)

            text += "{COLOR %02x}" % data[i]
            i += 1

        elif c >= 0xfa and c <= 0xfe and japanese:

            # Kanji
            if i >= dataSize:
                raise IndexError("Spurious kanji code %02x at end of kernel string %r" % (c, data))

            k = data[i]
            i += 1

            text += decodeKanji(c, k)

        else:

            raise IndexError("Illegal control code %02x in kernel string %r" % (c, data))

    return text


# Encode unicode string to FF7 text string.
def encode(text, field, japanese):
    if japanese:
        charset = normalCharsJP
    else:
        charset = normalChars

    textSize = len(text)
    data = bytearray()

    i = 0
    while i < textSize:
        c = text[i]
        i += 1

        if c == '\\':

            # Escape sequence
            if i >= textSize:
                raise IndexError("Spurious '\\' at end of string '%s'" % text)

            c = text[i]
            i += 1

            if c in escapeChars:
                data.append(charset.index(c))
            else:
                raise ValueError("Unknown escape sequence '\\%s' in string '%s'" % (c, text))

        elif c == '{':

            # Command sequence
            end = text.find('}', i)
            if end == -1:
                raise IndexError("Mismatched {} in string '%s'" % text)

            command = text[i:end]
            keyword = command.split()[0]
            i = end + 1

            if field:

                # Field command
                if keyword == 'WAIT':

                    # WAIT <arg>
                    m = re.match(r"WAIT (\d+)", command)
                    if not m:
                        raise ValueError("Syntax error in command '%s' in string '%s'" % (command, text))

                    arg = int(m.group(1))
                    if arg > 0xffff:
                        raise ValueError("Argument of WAIT command greater than 65535 in string '%s'" % text)

                    data.extend(b'\xfe\xdd')
                    data.extend(struct.pack("<H", arg))

                elif keyword == 'STR':

                    # STR <offset> <length>
                    m = re.match(r"STR ([a-fA-F0-9]{4}) ([a-fA-F0-9]{4})", command)
                    if not m:
                        raise ValueError("Syntax error in command '%s' in string '%s'" % (command, text))

                    offset = int(m.group(1), 16)
                    length = int(m.group(2), 16)

                    data.extend(b'\xfe\xe2')
                    data.extend(struct.pack("<HH", offset, length))

                else:

                    # Simple command without arguments
                    try:
                        code = fieldCommands['{' + command + '}']
                        data.extend(code)

                        # Strip extra newline after NEW command
                        if command == "NEW":
                            if (i < textSize) and (text[i] == '\n'):
                                i += 1

                    except KeyError:
                        raise ValueError("Unknown command '%s' in string '%s'" % (command, text))

            else:

                # Kernel command
                if keyword == 'COLOR':

                    # Text box color
                    m = re.match(r"COLOR ([a-fA-F0-9]{2})", command)
                    if not m:
                        raise ValueError("Syntax error in command '%s' in string '%s'" % (command, text))

                    data.append(0xf8)
                    data.append(int(m.group(1), 16))

                else:

                    # Kernel variable reference
                    found = False
                    for (code, checkKeyword,) in kernelVars.items():
                        if keyword == checkKeyword:
                            m = re.match(r"%s ([a-fA-F0-9]{2}) ([a-fA-F0-9]{2})" % keyword, command)
                            if not m:
                                raise ValueError("Syntax error in command '%s' in string '%s'" % (command, text))

                            data.append(code)
                            data.append(int(m.group(1), 16))
                            data.append(int(m.group(2), 16))

                            found = True
                            break

                    if not found:
                        raise ValueError("Unknown command '%s' in string '%s'" % (command, text))

        else:

            # Handle special field characters
            if field:
                if c == '\t':
                    data.append(0xe1)
                    continue
                elif c == '\n':
                    data.append(0xe7)
                    continue
                elif c == '〇':
                    data.append(0xf6)
                    continue
                elif c == '△':
                    data.append(0xf7)
                    continue
                elif c == '☐':
                    data.append(0xf8)
                    continue
                elif c == '✕':
                    data.append(0xf9)
                    continue
# TODO: Disabled for now since these shortcuts don't work in map names and
# are not particularly useful to begin with...
#                elif c == ',' and i < textSize and text[i] == ' ':
#                    data.append(0xe2)
#                    i += 1
#                    continue
#                elif c == '.' and i < textSize and text[i] == '"':
#                    data.append(0xe3)
#                    i += 1
#                    continue
#                elif c == '…' and i < textSize and text[i] == '"':
#                    data.append(0xe4)
#                    i += 1
#                    continue

            # Regular printable character
            try:
                data.append(charset.index(c))
            except ValueError:
                raise ValueError("Unencodable character '%s' in string '%s'" % (c, text))

    # Terminate string
    data.append(0xff)
    return bytes(data)


# Return the pixel width of a character.
def charWidth(c, fixed, metrics):
    if fixed:
        return 13
    else:
        m = metrics[c]
        return (m & 0x1f) + (m >> 5)  # width + kerning


# Determine the maximum pixel width and height required for displaying a field
# text string, returning a (width, height) tuple. The 'metrics' argument is an
# array of character width/kerning data, as found in the WINDOW.BIN archive.
def extent(text, metrics):
    maxCharacterNameLen = 9
    lineHeight = 16

    data = encode(text, True, False)
    dataSize = len(data)

    maxWidth = 0
    maxLines = 0

    lineWidth = 0
    numLines = 1

    fixed = False

    i = 0
    while i < dataSize:
        c = data[i]
        i += 1

        if c < 0xe0:

            # Regular character
            lineWidth += charWidth(c, fixed, metrics)

        elif c == 0xe0:

            # 10 spaces
            lineWidth += charWidth(0, fixed, metrics) * 10

        elif c == 0xe1:

            # 4 spaces
            lineWidth += charWidth(0, fixed, metrics) * 4

        elif c == 0xe2:

            # ', ' shortcut
            lineWidth += charWidth(0x0c, fixed, metrics) + charWidth(0, fixed, metrics)

        elif c == 0xe3:

            # '."' shortcut
            lineWidth += charWidth(0x0e, fixed, metrics) + charWidth(0x02, fixed, metrics)

        elif c == 0xe4:

            # '…"'
            lineWidth += charWidth(0xa9, fixed, metrics) + charWidth(0x02, fixed, metrics)

        elif c == 0xe7:

            # New line
            if lineWidth > maxWidth:
                maxWidth = lineWidth
            lineWidth = 0
            numLines += 1

        elif c == 0xe8:

            # New page
            if lineWidth > maxWidth:
                maxWidth = lineWidth
            lineWidth = 0

            if numLines > maxLines:
                maxLines = numLines
            numLines = 1

        elif c >= 0xea and c <= 0xf5:

            # Character name, assume it's filled with 'W's
            lineWidth += charWidth(0x37, fixed, metrics) * maxCharacterNameLen

        elif c >= 0xf6 and c <= 0xf9:

            # Controller button (estimated width)
            lineWidth += 16

        elif c == 0xfe:

            # Extended control code
            c = data[i]
            i += 1

            if c == 0xdd:

                # WAIT command, skip args
                i += 2

            elif c == 0xde or c == 0xe1:

                # Decimal variable, assume max. 5 digits (0..65535)
                lineWidth += charWidth(0x10, fixed, metrics) * 5  # '0'

            elif c == 0xdf:

                # Hexadecimal variable, assume max. 4 digits (0..FFFF)
                lineWidth += charWidth(0x21, fixed, metrics) * 4  # 'A'

            elif c == 0xe2:

                # STR command, get length and skip args
                length = struct.unpack_from("<H", data, i + 2)[0]
                i += 4

                lineWidth += charWidth(0x37, fixed, metrics) * length  # 'W'

            elif c == 0xe9:

                # Toggle fixed-width character spacing
                fixed = not fixed

    if lineWidth > maxWidth:
        maxWidth = lineWidth
    if numLines > maxLines:
        maxLines = numLines

    if maxLines > 13:
        maxLines = 13

    return (maxWidth, maxLines * lineHeight)
