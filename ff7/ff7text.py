# -*- coding: utf-8 -*-

#
# ff7.ff7text - Final Fantasy VII text manipulation
#
# Copyright (C) 2014 Christian Bauer <www.cebix.net>
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
    u" !\"#$%&'()*+,-./01234"
    u"56789:;<=>?@ABCDEFGHI"
    u"JKLMNOPQRSTUVWXYZ[\\]^"
    u"_`abcdefghijklmnopqrs"
    u"tuvwxyz{|}~ ÄÅÇÉÑÖÜáà"
    u"âäãåçéèêëíìîïñóòôöõúù"
    u"ûü♥°¢£↔→♪ßα  ´¨≠ÆØ∞±≤"  # '♥' (0x80), '↔' (0x84), '→' (0x85), '♪' (0x86), and 'α' (0x88) are additions
    u"≥¥µ∂ΣΠπ⌡ªºΩæø¿¡¬√ƒ≈∆«"
    u"»… ÀÃÕŒœ–—“”‘’÷◊ÿŸ⁄ ‹"
    u"›ﬁﬂ■‧‚„‰ÂÊÁËÈÍÎÏÌÓÔ Ò"
    u"ÚÛÙıˆ˜¯˘˙˚¸˝˛ˇ       "
)

# Japanese font texture 1, CLUT 0, upper half
normalCharsJP = (
    u"バばビびブぶベべボぼガがギぎグぐゲげゴごザ"
    u"ざジじズずゼぜゾぞダだヂぢヅづデでドどヴパ"
    u"ぱピぴプぷペぺポぽ0123456789、。"
    u" ハはヒひフふヘへホほカかキきクくケけコこ"
    u"サさシしスすセせソそタたチちツつテてトとウ"
    u"うアあイいエえオおナなニにヌぬネねノのマま"
    u"ミみムむメめモもラらリりルるレれロろヤやユ"
    u"ゆヨよワわンんヲをッっャゃュゅョょァぁィぃ"
    u"ゥぅェぇォぉ!?『』．+ABCDEFGHI"
    u"JKLMNOPQRSTUVWXYZ・*ー〜"
    u"…%/:&【】♥→αβ「」()-=   ⑬"
)

# Japanese font texture 1, CLUT 0, lower half
kanjiSet1 = (
    u"必殺技地獄火炎裁雷大怒斬鉄剣槍海衝聖審判転"
    u"生改暗黒釜天崩壊零式自爆使放射臭息死宣告凶"
    u"破晄撃画龍晴点睛超究武神覇癒風邪気封印吹烙"
    u"星守護命鼓動福音掌打水面蹴乱闘合体疾迅明鏡"
    u"止抜山蓋世血祭鎧袖一触者滅森羅万象装備器攻"
    u"魔法召喚獣呼出持相手物確率弱投付与変化片方"
    u"行決定分直前真似覚列後位置防御発回連続敵全"
    u"即効果尾毒消金針乙女興奮剤鎮静能薬英雄榴弾"
    u"右腕砂時計糸戦惑草牙南極冷結晶電鳥角有害質"
    u"爪光月反巨目砲重力球空双野菜実兵単毛茶色髪"
)

# Japanese font texture 1, CLUT 1, upper half
kanjiSet2 = (
    u"安香花会員蜂蜜館下着入先不子供屋商品景交換"
    u"階模型部離場所仲間無制限殿様秘氷河図何材料"
    u"雪上進事古代種鍵娘紙町住奥眠楽最初村雨釘陸"
    u"吉揮叢雲軍異常通威父蛇矛青偃刀戟十字裏車円"
    u"輪卍折鶴倶戴螺貝突銀玉正宗具甲烈属性吸収半"
    u"減土高級状態縁闇睡石徐々的指混呪開始歩復盗"
    u"小治理同速遅逃去視複味沈黙還倍数瀕取返人今"
    u"差誰当拡散飛以外暴避振身中旋津波育機械擲炉"
    u"新両本君洞内作警特殊板強穴隊族亡霊鎖足刃頭"
    u"怪奇虫跳侍左首潜長親衛塔宝条像忍謎般見報充"
    u"填完了銃元経験値終獲得名悲蛙操成費背切替割"
)

# Japanese font texture 1, CLUT 1, lower half
kanjiSet3 = (
    u"由閉記憶選番街底忘都過艇路運搬船基心港末宿"
    u"西道艦家乗竜巻迷宮絶壁支社久件想秒予多落受"
    u"組余系標起迫日勝形引現解除磁互口廃棄汚染液"
    u"活令副隠主斉登温泉百段熱走急降奪響嵐移危戻"
    u"遠吠軟骨言葉震叫噴舞狩粉失敗眼激盤逆鱗踏喰"
    u"盾叩食凍退木吐線魅押潰曲翼教皇太陽界案挑援"
    u"赤往殴意東北参知聞来仕別集信用思毎悪枯考然"
    u"張好伍早各独配腐話帰永救感故売浮市加流約宇"
    u"礼束母男年待宙立残俺少精士私険関倒休我許郷"
    u"助要問係旧固荒稼良議導夢追説声任柱満未顔旅"
)

# Japanese font texture 2, CLUT 0
kanjiSet4 = (
    u"友伝夜探対調民読占頼若学識業歳争苦織困答準"
    u"恐認客務居他再幸役縮情豊夫近窟責建求迎貸期"
    u"工算湿難保帯届凝笑向可遊襲申次国素題普密望"
    u"官泣創術演輝買途浴老幼利門格原管牧炭彼房驚"
    u"禁注整衆語証深層査渡号科欲店括坑酬緊研権書"
    u"暇兄派造広川賛駅絡在党岸服捜姉敷胸刑谷痛岩"
    u"至勢畑姿統略抹展示修酸製歓接障災室索扉傷録"
    u"優基讐勇司境璧医怖狙協犯資設雇根億脱富躍純"
    u"写病依到練順園総念維検朽圧補公働因朝浪祝恋"
    u"郎勉春功耳恵緑美辺昇悩泊低酒影競二矢瞬希志"
)

# Japanese font texture 2, CLUT 1
kanjiSet5 = (
    u"孫継団給抗違提断島栄油就僕存企比浸非応細承"
    u"編排努締談趣埋営文夏個益損額区寒簡遣例肉博"
    u"幻量昔臓負討悔膨飲妄越憎増枚皆愚療庫涙照冗"
    u"壇坂訳抱薄義騒奴丈捕被概招劣較析繁殖耐論貴"
    u"称千歴史募容噂壱胞鳴表雑職妹氏踊停罪甘健焼"
    u"払侵頃愛便田舎孤晩清際領評課勤謝才偉誤価欠"
    u"寄忙従五送周頑労植施販台度嫌諸習緒誘仮借輩"
    u"席戒弟珍酔試騎霜鉱裕票券専祖惰偶怠罰熟牲燃"
    u"犠快劇拠厄抵適程繰腹橋白処匹杯暑坊週秀看軽"
    u"棊和平王姫庭観航横帳丘亭財律布規謀積刻陥類"
)

def decodeKanji(bank, code):
    if bank == '\xfa':
        return kanjiSet1[code]
    elif bank == '\xfb':
        return kanjiSet2[code]
    elif bank == '\xfc':
        return kanjiSet3[code]
    elif bank == '\xfd':
        return kanjiSet4[code]
    elif bank == '\xfe':
        return kanjiSet5[code]

    raise IndexError, "Invalid kanji bank %02x" % bank


# Special characters of the field module (0xe0..0xff)
fieldSpecialChars = {

    # Not in Japanese version, where 0xe0..0xe6 are regular characters:
    '\xe0': u"{CHOICE}",    # choice tab (10 spaces)
    '\xe1': u"\t",          # tab (4 spaces)
    '\xe2': u", ",          # shortcut
    '\xe3': u'."',          # not very useful shortcut with the wrong quote character...
    '\xe4': u'…"',          # not very useful shortcut with the wrong quote character...

    # In all versions
    '\xe6': u"⑬",           # appears in the US version of BLACKBG6, presumably a mistake
    '\xe7': u"\n",          # new line
    '\xe8': u"{NEW}",       # new page

    '\xea': u"{CLOUD}",
    '\xeb': u"{BARRET}",
    '\xec': u"{TIFA}",
    '\xed': u"{AERITH}",
    '\xee': u"{RED XIII}",
    '\xef': u"{YUFFIE}",
    '\xf0': u"{CAIT SITH}",
    '\xf1': u"{VINCENT}",
    '\xf2': u"{CID}",
    '\xf3': u"{PARTY #1}",
    '\xf4': u"{PARTY #2}",
    '\xf5': u"{PARTY #3}",

    '\xf6': u"〇",          # controller button
    '\xf7': u"△",           # controller button
    '\xf8': u"☐",           # controller button
    '\xf9': u"✕",           # controller button

    '\xfa': u"",            # kanji 1
    '\xfb': u"",            # kanji 2
    '\xfc': u"",            # kanji 3
    '\xfd': u"",            # kanji 4

    # '\xfe'                # extended control code, see below
    # '\xff'                # end of string
}

# Extended control codes of the field module (0xfe ..)
fieldControlCodes = {
    '\xd2': u"{GRAY}",
    '\xd3': u"{BLUE}",
    '\xd4': u"{RED}",
    '\xd5': u"{PURPLE}",
    '\xd6': u"{GREEN}",
    '\xd7': u"{CYAN}",
    '\xd8': u"{YELLOW}",
    '\xd9': u"{WHITE}",
    '\xda': u"{FLASH}",
    '\xdb': u"{RAINBOW}",

    '\xdc': u"{PAUSE}",   # pause until OK button is pressed
    # '\xdd'              # wait # of frames
    '\xde': u"{NUM}",     # decimal variable
    '\xdf': u"{HEX}",     # hex variable
    '\xe0': u"{SCROLL}",  # wait for OK butten, then scroll window
    '\xe1': u"{RNUM}",    # decimal variable, right-aligned
    # '\xe2'              # value from game state memory
    '\xe9': u"{FIXED}",   # fixed-width character spacing on/off
}

# Inverse mapping of field module commands to codes
fieldCommands = {v:k for k, v in fieldSpecialChars.iteritems() if v}
fieldCommands.update({v:('\xfe' + k) for k, v in fieldControlCodes.iteritems()})

# Characters which must be escaped when decoding
escapeChars = u"\\{}"


# Decode FF7 field text string to unicode string.
def decodeField(data, japanese = False):
    if japanese:
        charset = normalCharsJP
        numNormalChars = '\xe7'
    else:
        charset = normalChars
        numNormalChars = '\xe0'

    dataSize = len(data)
    text = u""

    i = 0
    while i < dataSize:
        c = data[i]
        i += 1

        if c == '\xff':

            # End of string
            break

        elif c < numNormalChars:

            # Regular printable character
            t = charset[ord(c)]

            if t in escapeChars:
                text += u"\\"

            text += t

        elif c >= '\xfa' and c <= '\xfd' and japanese:

            # Kanji
            if i >= dataSize:
                raise IndexError, "Spurious kanji code %02x at end of string %r" % (ord(c), data)

            k = data[i]
            i += 1

            text += decodeKanji(c, ord(k))

        elif c == '\xfe':

            # Field module control code or kanji
            if i >= dataSize:
                raise IndexError, "Spurious control code %02x at end of string %r" % (ord(c), data)

            k = data[i]
            i += 1

            if k < '\xd2' and japanese:

                text += decodeKanji(c, ord(k))

            elif k == '\xdd':

                # WAIT <arg> command
                if i >= dataSize - 1:
                    raise IndexError, "Spurious WAIT command at end of string %r" % data

                arg = struct.unpack_from("<H", data, i)
                i += 2

                text += u"{WAIT %d}" % arg

            elif k == '\xe2':

                # STR <offset> <length> command
                if i >= dataSize - 3:
                    raise IndexError, "Spurious STR command at end of string %r" % data

                offset, length = struct.unpack_from("<HH", data, i)
                i += 4

                text += u"{STR %04x %04x}" % (offset, length)

            else:

                # Other control code
                if not k in fieldControlCodes:
                    raise IndexError, "Illegal control code %02x in field string %r" % (ord(k), data)

                text += fieldControlCodes[k]
                
        else:

            # Field module special character
            t = fieldSpecialChars[c]

            if not t:
                raise IndexError, "Illegal character %02x in field string %r" % (ord(c), data)

            if c == '\xe8':  # newline after {NEW}
                t += '\n'

            text += t

    return text


# Control codes referencing kernel variables
kernelVars = {
    '\xea': u"CHAR",
    '\xeb': u"ITEM",
    '\xec': u"NUM",
    '\xed': u"TARGET",
    '\xee': u"ATTACK",
    '\xef': u"ID",
    '\xf0': u"ELEMENT",
}


# Decode FF7 kernel text string to unicode string.
def decodeKernel(data, japanese = False):
    if japanese:
        charset = normalCharsJP
    else:
        charset = normalChars

    dataSize = len(data)
    text = u""

    i = 0
    while i < dataSize:
        c = data[i]
        i += 1

        if c == '\xff':

            # End of string
            break

        elif c < '\xe7':

            # Regular printable character
            t = charset[ord(c)]

            if t in escapeChars:
                text += u"\\"

            text += t

        elif c >= '\xea' and c <= '\xf0':

            # Kernel variable
            if i >= dataSize - 1:
                raise IndexError, "Spurious control code %02x at end of kernel string %r" % (ord(c), data)

            text += u"{%s %02x %02x}" % (kernelVars[c], ord(data[i]), ord(data[i+1]))
            i += 2

        elif c == '\xf8':

            # Text box color
            if i >= dataSize:
                raise IndexError, "Spurious color code at end of kernel string %r" % data

            text += u"{COLOR %02x}" % ord(data[i])
            i += 1

        elif c >= '\xfa' and c <= '\xfe' and japanese:

            # Kanji
            if i >= dataSize:
                raise IndexError, "Spurious kanji code %02x at end of kernel string %r" % (ord(c), data)

            k = data[i]
            i += 1

            text += decodeKanji(c, ord(k))

        else:

            raise IndexError, "Illegal control code %02x in kernel string %r" % (ord(c), data)

    return text


# Encode unicode string to FF7 text string.
def encode(text, field, japanese):
    if japanese:
        charset = normalCharsJP
    else:
        charset = normalChars

    textSize = len(text)
    data = ""

    i = 0
    while i < textSize:
        c = text[i]
        i += 1

        if c == u'\\':

            # Escape sequence
            if i >= textSize:
                raise IndexError, "Spurious '\\' at end of string '%s'" % text

            c = text[i]
            i += 1

            if c in escapeChars:
                data += chr(charset.index(c))
            else:
                raise ValueError, "Unknown escape sequence '\\%s' in string '%s'" % (c, text)

        elif c == u'{':

            # Command sequence
            end = text.find(u'}', i)
            if end == -1:
                raise IndexError, "Mismatched {} in string '%s'" % text

            command = text[i:end]
            keyword = command.split()[0]
            i = end + 1

            if field:

                # Field command
                if keyword == u'WAIT':

                    # WAIT <arg>
                    m = re.match(r"WAIT (\d+)", command)
                    if not m:
                        raise ValueError, "Syntax error in command '%s' in string '%s'" % (command, text)

                    arg = int(m.group(1))
                    if arg > 0xffff:
                        raise ValueError, "Argument of WAIT command greater than 65535 in string '%s'" % text

                    data += '\xfe\xdd'
                    data += struct.pack("<H", arg)

                elif keyword == u'STR':

                    # STR <offset> <length>
                    m = re.match(r"STR ([a-fA-F0-9]{4}) ([a-fA-F0-9]{4})", command)
                    if not m:
                        raise ValueError, "Syntax error in command '%s' in string '%s'" % (command, text)

                    offset = int(m.group(1), 16)
                    length = int(m.group(2), 16)

                    data += '\xfe\xe2'
                    data += struct.pack("<HH", offset, length)

                else:

                    # Simple command without arguments
                    try:
                        code = fieldCommands['{' + command + '}']
                        data += code

                        # Strip extra newline after NEW command
                        if command == "NEW":
                            if (i < textSize) and (text[i] == u'\n'):
                                i += 1

                    except KeyError:
                        raise ValueError, "Unknown command '%s' in string '%s'" % (command, text)

            else:

                # Kernel command
                if keyword == u'COLOR':

                    # Text box color
                    m = re.match(r"COLOR ([a-fA-F0-9]{2})", command)
                    if not m:
                        raise ValueError, "Syntax error in command '%s' in string '%s'" % (command, text)

                    data += '\xf8'
                    data += chr(int(m.group(1), 16))

                else:

                    # Kernel variable reference
                    found = False
                    for (code, checkKeyword,) in kernelVars.iteritems():
                        if keyword == checkKeyword:
                            m = re.match(r"%s ([a-fA-F0-9]{2}) ([a-fA-F0-9]{2})" % keyword, command)
                            if not m:
                                raise ValueError, "Syntax error in command '%s' in string '%s'" % (command, text)

                            data += code
                            data += chr(int(m.group(1), 16))
                            data += chr(int(m.group(2), 16))

                            found = True
                            break

                    if not found:
                        raise ValueError, "Unknown command '%s' in string '%s'" % (command, text)

        else:

            # Handle special field characters
            if field:
                if c == u'\t':
                    data += '\xe1'
                    continue
                elif c == u'\n':
                    data += '\xe7'
                    continue
                elif c == u'〇':
                    data += '\xf6'
                    continue
                elif c == u'△':
                    data += '\xf7'
                    continue
                elif c == u'☐':
                    data += '\xf8'
                    continue
                elif c == u'✕':
                    data += '\xf9'
                    continue
# TODO: Disabled for now since these shortcuts don't work in map names and
# are not particularly useful to begin with...
#                elif c == u',' and i < textSize and text[i] == u' ':
#                    data += '\xe2'
#                    i += 1
#                    continue
#                elif c == u'.' and i < textSize and text[i] == u'"':
#                    data += '\xe3'
#                    i += 1
#                    continue
#                elif c == u'…' and i < textSize and text[i] == u'"':
#                    data += '\xe4'
#                    i += 1
#                    continue

            # Regular printable character
            try:
                data += chr(charset.index(c))
            except ValueError:
                raise ValueError, "Unencodable character '%s' in string '%s'" % (c, text)

    # Terminate string
    return data + '\xff'


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
        c = ord(data[i])
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
            c = ord(data[i])
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
