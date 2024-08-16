# -*- coding: utf-8 -*-

#
# wa.text - Wild Arms text manipulation
#
# Copyright (C) Christian Bauer <www.cebix.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import re
import zlib

from version import Version, isJapanese


# Text control codes
controlCodes = [

    # (argLen, code)
    (0, u"0x00"),
    (1, u"STR"),       # 0x01 xx       - string parameter
    (1, u"NUM"),       # 0x02 xx       - signed numeric parameter
    (1, u"UNUM"),      # 0x03 xx       - unsigned numeric parameter
    (1, u"HEX"),       # 0x04 xx       - hexadecimal parameter
    (1, u"CHAR"),      # 0x05 xx       - character name
    (1, u"ITEM"),      # 0x06 xx       - item name
    (1, u"SPELL"),     # 0x07 xx       - spell name
    (1, u"ITEMICON"),  # 0x08 xx       - item icon
    (1, u"SPELLICON"), # 0x09 xx       - spell icon
    (1, u"TOOL"),      # 0x0a xx       - tool name
    (1, u"TOOLICON"),  # 0x0b xx       - tool icon
    (0, u"CLEAR"),     # 0x09          - clear window
    (0, u"CR"),        # 0x0d          - new line
    (0, u"SMALL"),     # 0x0e          - switch to regular small (12x12) font (JP only)
    (0, u"SCROLL"),    # 0x0f          - scroll up 1 line
    (0, u"PAUSE"),     # 0x10          - pause until OK button is pressed
    (1, u"COLOR"),     # 0x11 xx       - set text color
    (3, u"SOUND"),     # 0x12 xx xx xx - play sound effect
    (0, u"NOP"),       # 0x13          - nop
    (0, u"LARGE"),     # 0x14          - switch to large (16x16) font (JP only)
    (2, u"SPEED"),     # 0x15 xx xx    - set text speed
    (2, u"WAIT"),      # 0x16 xx xx    - wait xxxx frames
    (0, u"CONTINUE"),  # 0x17          - continue automatically after message (don't pause)
    (0, u"XSHADOW"),   # 0x18          - toggle text shadow in X direction
    (0, u"YSHADOW"),   # 0x19          - toggle text shadow in Y direction
    (1, u"ASK"),       # 0x1a xx       - ask question
    (0, u"ASYNC"),     # 0x1b          - continue script while message is being displayed
    (0, u"0x1c"),
    (0, u"0x1d"),
    (0, u"0x1e"),
    (0, u"0x1f"),
]

# Inverse mapping of commands to control codes
codeOfCommand = {controlCodes[i][1]:i for i in xrange(len(controlCodes))}


# Decode text control code, returning a (code, new_index) tuple.
def decodeControl(c, data, index):
    argLen, code = controlCodes[c]

    arg = data[index:index + argLen]

    if argLen > 0:
        code = code + u' ' + arg.decode("ascii")

    return (u'{' + code + u'}', index + argLen)


# Katakana table (like Shift-JIS but full-width)
katakana = (
    u"ァィゥェォャュョッーアイウエオカ"  # a7..b6
    u"キクケコサシスセソタチツテトナニ"  # b7..c6
    u"ヌネノハヒフヘホマミムメモヤユヨ"  # c7..d6
    u"ラリルレロワン"                    # d7..dd
)

# Kanji table bank 1 (88 xx)
kanji1 = (
      u"持道具使各特殊装備武器防身戦闘時行動傾向指示状態任意変更回復味"  # 01..1f
    u"方単体不能完全毒治療病気魔力封印混乱忘却異常冒険一中断者逮捕会員"  # 20..3f
    u"証度町便利地図表出裏残弾数値補給早撃消費軽減法記録腕上昇反応加工"  # 40..5f
    u"合鍵修得経験倍化右手用無効属性果通攻付与水火風雷心聖代歩前進確率"  # 60..7f
    u"打避運伝説左書敵吸収頭部静炎花妻品失巨人善悪薬草古増幅置竜神像獅"  # 80..9f
    u"子王女言葉本名仕強白石胸宝声紋登呼魂三種俺必帰込刻柱結界小型発射"  # a0..bf
    u"拡散照連続精感式高焼夷携帯荷電粒砲空間作相転位兵同抜刀衝波物盗峰"  # c0..df
    u"半分命後放切定剣宿解牙貫影技広範囲次元狭現換札山脈渡落下岩碑"      # e0..fd
)

# Kanji table bank 2 (89 xx)
kanji2 = (
      u"謎試練壊機械浪士館授騎留思念超眠御抵抗還姿自除問入口戻調閉低霊"  # 01..1f
    u"球止爆保護形訪瞬移去集様受在最大段守割替音楽整理頓何選択障害吹飛"  # 20..3f
    u"探知速可繰的爪多目色秘暖光限計議話杖村院城港場船基房森塚憶遺跡棺"  # 40..5f
    u"殿死迷宮号庭園海深淵堕天廊廃屋夢幻島祭壇雪峡谷別複写直活管画面終"  # 60..7f
    u"了先容量削読逃隊列予枠内他旅少年敗制尽獲弱点取起着闇支援接生殺順"  # 80..9f
    u"番決未烈閃暴周致禁呪文紫改危質急論象金粉実菌糸導我流字斬奥義凶刃"  # a0..bf
    u"舞陣夜叉奇宇宙振怪線翼氷巻裂仲走潜覚醒詠唱"                        # c0..d4
)

# Mapping of Kanji bitmap hash (CRC32) to unicode
kanjiByHash = {
    0x0004e407: u'住', 0x0040a586: u'鼓', 0x008bd144: u'鎧', 0x0121a417: u'中',
    0x01ccd1a4: u'令', 0x0216cca9: u'礎', 0x02385585: u'届', 0x023c1223: u'配',
    0x024aabe7: u'慎', 0x027674a1: u'爆', 0x02a05095: u'篇', 0x02b82810: u'妬',
    0x02bf5738: u'準', 0x02dac8cc: u'西', 0x02e54b3c: u'労', 0x034d30ea: u'重',
    0x0369ae46: u'拠', 0x03855552: u'荒', 0x040cbd14: u'幽', 0x0430ce9e: u'封',
    0x0443f560: u'半', 0x0481aa67: u'雄', 0x04a93452: u'語', 0x04f8ad58: u'霊',
    0x05038f66: u'堅', 0x05442e2a: u'削', 0x0549fe53: u'謀', 0x055b5ce2: u'夢',
    0x05950820: u'詰', 0x059f9e11: u'範', 0x05ac91e9: u'野', 0x05c33cd6: u'店',
    0x05e85590: u'誠', 0x0617875a: u'法', 0x0619a7ed: u'妙', 0x0655a0c1: u'七',
    0x065de255: u'窓', 0x06bcac11: u'習', 0x06e62626: u'芽', 0x0713f98d: u'二',
    0x0717bddf: u'宏', 0x07321911: u'滞', 0x0764b621: u'帰', 0x07b6d7ec: u'鎖',
    0x07e140ad: u'歩', 0x07e1a1e6: u'都', 0x07f589b5: u'記', 0x0858a548: u'冠',
    0x08822518: u'埋', 0x0894b125: u'滅', 0x089f914c: u'独', 0x08c6690e: u'泊',
    0x090bb6a3: u'練', 0x0916b682: u'析', 0x091f5aab: u'問', 0x096928e3: u'組',
    0x098c18f2: u'徳', 0x0998fd60: u'彼', 0x09a2f81d: u'理', 0x09a93a8d: u'渇',
    0x09c8fcf0: u'勉', 0x09edb2f9: u'期', 0x09f8867e: u'弱', 0x09ff6c1d: u'姿',
    0x0a6622c2: u'浸', 0x0ad5c09a: u'十', 0x0ae78b1e: u'寸', 0x0b5446d8: u'究',
    0x0bf3dec2: u'統', 0x0c1405d1: u'縮', 0x0c3984b0: u'房', 0x0c3c8bd2: u'迷',
    0x0c806bb5: u'騒', 0x0c86586d: u'寄', 0x0d2845a3: u'頑', 0x0d3093b5: u'匹',
    0x0d3c7ec8: u'盛', 0x0db9f593: u'降', 0x0dd34472: u'図', 0x0e03297a: u'方',
    0x0e31308b: u'演', 0x0e51fa88: u'玄', 0x0ef2244b: u'射', 0x0f135d9b: u'同',
    0x0f14795c: u'微', 0x104c4b14: u'柄', 0x109187ab: u'集', 0x110e7582: u'嬢',
    0x1127e974: u'命', 0x11ba4826: u'隊', 0x11da5e33: u'迎', 0x11fc44e1: u'転',
    0x1204d59e: u'伯', 0x120df1c4: u'歓', 0x1213a7f6: u'富', 0x12373aa8: u'整',
    0x1248d3d0: u'臨', 0x12d0008c: u'吸', 0x12e16534: u'白', 0x12f6f127: u'点',
    0x1311e686: u'御', 0x13586d87: u'求', 0x135b4ca6: u'戻', 0x13965e25: u'抱',
    0x139e92c3: u'掘', 0x13a03724: u'誤', 0x13d426a2: u'新', 0x14087d76: u'故',
    0x1412332b: u'林', 0x14c85377: u'訓', 0x150bcb42: u'顔', 0x15491d83: u'凶',
    0x155910ef: u'数', 0x156035d2: u'飯', 0x15b86c66: u'収', 0x15ca2237: u'破',
    0x15d45209: u'略', 0x165067d5: u'館', 0x1660603b: u'騎', 0x16897c12: u'永',
    0x16a60232: u'崩', 0x16aab0fc: u'了', 0x16e508c6: u'固', 0x16f59e05: u'試',
    0x171a8caf: u'輩', 0x1739a61f: u'限', 0x1762c681: u'遊', 0x17badac7: u'刀',
    0x17d426a5: u'将', 0x17dcc040: u'亀', 0x181ef792: u'郊', 0x18351efd: u'抹',
    0x18618a74: u'娘', 0x18bf9770: u'歪', 0x1928179d: u'机', 0x192a3d52: u'体',
    0x19d501c2: u'徐', 0x19f2c6ee: u'赴', 0x19f878c4: u'軌', 0x19f9fdba: u'缶',
    0x1a77c209: u'死', 0x1a8d74a7: u'太', 0x1aa14a13: u'危', 0x1ac53bbc: u'泣',
    0x1ac65897: u'注', 0x1b005165: u'機', 0x1b0a6278: u'紹', 0x1b10c9a5: u'特',
    0x1b298aec: u'偉', 0x1b643a6e: u'銀', 0x1b97e768: u'則', 0x1be9536c: u'魅',
    0x1c233a39: u'史', 0x1c6879b4: u'福', 0x1cafda57: u'埒', 0x1d54c7fa: u'両',
    0x1d72b957: u'景', 0x1d97a6b2: u'規', 0x1dac0764: u'甲', 0x1e25ebad: u'劇',
    0x1e371159: u'冊', 0x1e4efd3a: u'学', 0x1e80fbbd: u'遠', 0x1f25c76c: u'鉄',
    0x1f87934e: u'強', 0x1f9fc6bf: u'昨', 0x1fb18b4a: u'汝', 0x2087125b: u'脳',
    0x208ccb48: u'移', 0x20f2729a: u'亜', 0x210e8489: u'島', 0x21253585: u'素',
    0x216b22e0: u'加', 0x216da260: u'成', 0x21c4b4d6: u'際', 0x2204687a: u'祈',
    0x227c0829: u'乏', 0x227c553f: u'号', 0x22a017fa: u'鋭', 0x22c47329: u'刻',
    0x22db106a: u'衰', 0x22db36b0: u'亡', 0x22fb4b39: u'模', 0x2315b336: u'姉',
    0x232ae583: u'酋', 0x23d6b5dd: u'仮', 0x23f33497: u'捜', 0x2401a54b: u'欲',
    0x2415e9b5: u'惜', 0x243b718d: u'捕', 0x245b41d1: u'考', 0x24e70688: u'突',
    0x2520a949: u'台', 0x2535ff97: u'器', 0x254ae645: u'殊', 0x2553e93e: u'山',
    0x2555fb54: u'盟', 0x25c7ecdf: u'浅', 0x25dd4daa: u'抑', 0x2603aa1c: u'唱',
    0x26157bba: u'僕', 0x2681fa57: u'仕', 0x269ad173: u'痴', 0x26e34115: u'楽',
    0x26e858c7: u'管', 0x27200cae: u'航', 0x272b9f7e: u'苦', 0x275ba155: u'近',
    0x278a4217: u'厚', 0x278e0eb9: u'容', 0x2796c081: u'字', 0x27b085a7: u'猛',
    0x27b4d1f2: u'天', 0x27cbd264: u'震', 0x2816810a: u'皮', 0x288cb8f9: u'味',
    0x28cfa472: u'測', 0x28eb9551: u'位', 0x291c2c7b: u'終', 0x292886a9: u'冷',
    0x292a8a59: u'械', 0x2946eb93: u'吟', 0x299f65da: u'週', 0x29a438f0: u'拡',
    0x29e05be5: u'赦', 0x29e729ff: u'夫', 0x2a20efd3: u'粗', 0x2a23405f: u'舎',
    0x2a61b800: u'碑', 0x2a6cf7d7: u'護', 0x2a7d45e8: u'説', 0x2aca9572: u'下',
    0x2adf1bf8: u'妹', 0x2b15fe3a: u'大', 0x2b700819: u'委', 0x2b7b98ae: u'腹',
    0x2c14cc90: u'捨', 0x2c377dd4: u'冶', 0x2c7e5bf1: u'得', 0x2cc9bcd7: u'壊',
    0x2cd15301: u'改', 0x2cea9f0b: u'倉', 0x2d05dde9: u'急', 0x2d245666: u'帯',
    0x2daf7a8b: u'運', 0x2dca695d: u'杯', 0x2ddad0b2: u'次', 0x2e33fa27: u'似',
    0x2f24afc2: u'分', 0x2f4467f0: u'走', 0x2f53b03b: u'造', 0x2f776dad: u'失',
    0x2f9eea6c: u'折', 0x2fcf5e85: u'宝', 0x2fefdfba: u'占', 0x30092e6d: u'箱',
    0x30324e2b: u'出', 0x3093698b: u'触', 0x3098f717: u'個', 0x30d74747: u'叫',
    0x3113552e: u'牧', 0x31289ad4: u'商', 0x3193b0c6: u'廃', 0x31ac08db: u'預',
    0x32964a08: u'室', 0x32ae92e5: u'輝', 0x32b4f4ed: u'努', 0x3318d664: u'飼',
    0x33720cbe: u'乗', 0x338233d8: u'切', 0x33adf80c: u'松', 0x34417b14: u'絆',
    0x346a8b22: u'弟', 0x34748f1d: u'覇', 0x34a23ec4: u'田', 0x34f58ae9: u'砂',
    0x3508dbf0: u'雨', 0x350ab097: u'宮', 0x35230e3d: u'極', 0x35a6d56c: u'託',
    0x35a94795: u'葉', 0x35fdd1a3: u'純', 0x362af680: u'輸', 0x36347c05: u'若',
    0x3685d12a: u'株', 0x36918749: u'浪', 0x36c5e84a: u'庫', 0x36dea405: u'髪',
    0x372d7ab1: u'偶', 0x372df1b6: u'貌', 0x374da768: u'殺', 0x375bc718: u'莫',
    0x37a0a9b7: u'沈', 0x380288bc: u'産', 0x3882d953: u'幡', 0x38ca320a: u'利',
    0x38d419ce: u'岩', 0x38e55a3d: u'開', 0x3927ba0a: u'船', 0x396b04a7: u'枯',
    0x397f68d5: u'慈', 0x399655c3: u'父', 0x399ccbd1: u'扉', 0x39ba0ac6: u'団',
    0x39d75130: u'院', 0x3a053caf: u'勝', 0x3a595328: u'済', 0x3a8fa223: u'根',
    0x3aa923df: u'奪', 0x3aaa59d9: u'尽', 0x3ab7622a: u'区', 0x3abb6a52: u'鳥',
    0x3ad4b838: u'訴', 0x3ae34f2f: u'階', 0x3aee008b: u'秒', 0x3af93a6c: u'編',
    0x3b128ad2: u'拓', 0x3b398013: u'懲', 0x3b6b9d8f: u'差', 0x3b7514c7: u'在',
    0x3b9b8235: u'勘', 0x3c0a450a: u'取', 0x3c637695: u'審', 0x3c85e696: u'咲',
    0x3cd87aee: u'災', 0x3d10234f: u'久', 0x3d2564cd: u'羽', 0x3d2c31ce: u'鉱',
    0x3d54e05d: u'便', 0x3d585dc8: u'怪', 0x3d5c041c: u'看', 0x3d84d41b: u'償',
    0x3dc342d3: u'井', 0x3e2b97ca: u'湖', 0x3e40b8fe: u'己', 0x3e62a047: u'晴',
    0x3eedebd8: u'全', 0x3f0ae4d5: u'席', 0x3f2d118c: u'五', 0x3f2f1f55: u'仁',
    0x3f594110: u'氏', 0x3f8a87e0: u'無', 0x3fb3e400: u'傷', 0x3fbda68d: u'揃',
    0x3fda5d5e: u'宣', 0x4023f975: u'建', 0x406a69e0: u'醒', 0x40a4c82a: u'況',
    0x40c7178a: u'聴', 0x40cf28ca: u'群', 0x40f924b8: u'辛', 0x416776c7: u'塩',
    0x416e3c12: u'竹', 0x4178e848: u'有', 0x4196b4c1: u'笑', 0x41a6bb28: u'続',
    0x41c6d367: u'候', 0x4238724d: u'栗', 0x4245448d: u'包', 0x428c4c76: u'私',
    0x429942c9: u'花', 0x42dcf065: u'簡', 0x42de90e3: u'必', 0x437e4e45: u'渉',
    0x43a9d728: u'貫', 0x43ce537d: u'援', 0x442ff962: u'誌', 0x444afad4: u'菌',
    0x446bd791: u'米', 0x44715f2e: u'休', 0x4474280e: u'換', 0x44882cad: u'報',
    0x44909590: u'至', 0x44941a39: u'嫌', 0x44bc1e6a: u'婦', 0x44d4392f: u'抗',
    0x44dce76f: u'話', 0x4547f95f: u'宅', 0x45af05fe: u'葬', 0x45c40c9e: u'逃',
    0x45caf652: u'庶', 0x45cf915b: u'臣', 0x45eceef6: u'消', 0x4611b986: u'最',
    0x46231aeb: u'信', 0x4664d29e: u'散', 0x4676f8be: u'四', 0x46bea61e: u'専',
    0x46db032d: u'盾', 0x46eb5d53: u'沿', 0x4714e7eb: u'春', 0x4781dcd0: u'質',
    0x47aa70ad: u'献', 0x47cc5044: u'具', 0x47ce5fb1: u'牢', 0x47d50e25: u'執',
    0x4825eb71: u'袋', 0x487e4713: u'我', 0x48c48408: u'殼', 0x48de90b7: u'争',
    0x49565ac8: u'途', 0x49911237: u'撃', 0x49a28759: u'紛', 0x49c87691: u'倫',
    0x49e003ef: u'伊', 0x4a1801c3: u'世', 0x4a220a8a: u'戴', 0x4a64d466: u'認',
    0x4a8befdc: u'讐', 0x4aa5330d: u'宿', 0x4ab2ac10: u'緒', 0x4aebe29d: u'設',
    0x4b334111: u'満', 0x4b669f95: u'溶', 0x4b742fbc: u'頭', 0x4bbbccdf: u'紀',
    0x4bdec539: u'各', 0x4c204e65: u'涯', 0x4c2a1e02: u'火', 0x4d2fce5b: u'遺',
    0x4d44f76b: u'峰', 0x4d87bf00: u'効', 0x4dc497f3: u'持', 0x4ddf03c2: u'講',
    0x4e059267: u'友', 0x4e187961: u'作', 0x4e4a71b2: u'吉', 0x4e56230a: u'交',
    0x4e5fcaec: u'象', 0x4eacab1b: u'茶', 0x4eba2ed6: u'険', 0x4edd8d42: u'細',
    0x4f47f767: u'譲', 0x4f4acf43: u'着', 0x4f551dd1: u'験', 0x4f5d1b12: u'定',
    0x4f859c54: u'歳', 0x4fec32be: u'陽', 0x4ffb2005: u'鍵', 0x501ebc0d: u'意',
    0x502b49cb: u'自', 0x5048abc5: u'余', 0x50be4f32: u'蓄', 0x510699f9: u'繰',
    0x511baa13: u'合', 0x513e1b9d: u'砦', 0x514c0e60: u'単', 0x518849fc: u'聖',
    0x51b34609: u'征', 0x51cf3d18: u'前', 0x51e7ea54: u'先', 0x52e1b297: u'掃',
    0x53260d8b: u'議', 0x53366a4d: u'城', 0x53376231: u'返', 0x534b45e4: u'公',
    0x534e2341: u'氷', 0x53554567: u'句', 0x539d1138: u'悦', 0x53ab46e3: u'該',
    0x53d9269f: u'旧', 0x53ff4ff5: u'壇', 0x54314f5d: u'王', 0x547b9bf8: u'昔',
    0x549205e0: u'座', 0x54dd7fc3: u'燃', 0x550ff180: u'障', 0x554eab57: u'牲',
    0x5560ce8e: u'副', 0x5566ce4b: u'代', 0x55697b05: u'除', 0x5588b73a: u'製',
    0x558de3b3: u'仰', 0x55999cf4: u'以', 0x559b958d: u'界', 0x55c474a9: u'短',
    0x55fa1b3d: u'央', 0x5602c0aa: u'長', 0x563de018: u'潜', 0x564a4663: u'拳',
    0x5676bff4: u'級', 0x568366f7: u'扱', 0x569b27b4: u'漠', 0x56a9a744: u'晩',
    0x56b023fe: u'積', 0x56fc500a: u'渦', 0x572c3720: u'索', 0x5788b66e: u'採',
    0x57c6496d: u'暖', 0x57c92f47: u'防', 0x57d678e8: u'残', 0x57e79752: u'幼',
    0x57f4b607: u'神', 0x581d6d7e: u'喰', 0x583f4507: u'嵐', 0x58538c01: u'鬼',
    0x58ef04d1: u'植', 0x58f2c329: u'漫', 0x594a0c19: u'継', 0x594e632d: u'章',
    0x596b7938: u'没', 0x599195e8: u'兵', 0x59c7c4fd: u'絡', 0x59c9a9b7: u'種',
    0x59df934b: u'男', 0x59e49d69: u'込', 0x59e4c6c7: u'順', 0x59fd8a57: u'式',
    0x5a15e03d: u'訳', 0x5a74db96: u'変', 0x5b1aae46: u'職', 0x5b52c28c: u'奏',
    0x5ba28b2c: u'涙', 0x5c585cd1: u'完', 0x5c65ff8c: u'員', 0x5c6fd7d0: u'厳',
    0x5c7128ad: u'送', 0x5cb83562: u'阻', 0x5cd71f43: u'離', 0x5cf03d8c: u'医',
    0x5d022b36: u'払', 0x5d1be06f: u'病', 0x5d7aa217: u'士', 0x5d7dbdaa: u'甘',
    0x5d93e521: u'辺', 0x5d9e2512: u'誰', 0x5d9fc8c5: u'度', 0x5de1c91d: u'察',
    0x5de96cf1: u'囲', 0x5e1d6c0d: u'毒', 0x5e2de501: u'陸', 0x5e2debc2: u'革',
    0x5e61d49d: u'廊', 0x5e6f2eed: u'迫', 0x5e9b3492: u'結', 0x5ecc2244: u'責',
    0x5ed56a65: u'門', 0x5ee793e7: u'伝', 0x5f5c649e: u'後', 0x5f93c05b: u'直',
    0x5fbf86dc: u'技', 0x5fdced23: u'華', 0x5fe2a3a5: u'如', 0x5fe64f0f: u'耳',
    0x6003dffc: u'癒', 0x6010f487: u'爵', 0x606d99f2: u'冗', 0x60716665: u'錬',
    0x609b3d38: u'基', 0x60c8c21f: u'妖', 0x60c99194: u'所', 0x60d19a94: u'停',
    0x60d6fb4b: u'陰', 0x60ee86b7: u'筋', 0x61087856: u'犠', 0x61236941: u'使',
    0x618026c2: u'渓', 0x61baa57e: u'班', 0x61d14300: u'癖', 0x6238df4e: u'業',
    0x624b2a6b: u'普', 0x624caec4: u'伏', 0x628ab57a: u'江', 0x62a5ea14: u'紋',
    0x62b70d12: u'欠', 0x632e5be9: u'恨', 0x63f25923: u'宴', 0x641a7d72: u'然',
    0x648e46e7: u'塊', 0x64cf6bd0: u'染', 0x65187bf4: u'追', 0x65305dcb: u'復',
    0x655aabf1: u'難', 0x659f7cc5: u'症', 0x65a9c839: u'踊', 0x65b2bba7: u'疑',
    0x65f51761: u'魂', 0x66031b38: u'勤', 0x664fcf1e: u'遭', 0x66538e3d: u'斬',
    0x66700d71: u'庵', 0x66a1c35f: u'本', 0x66a76e8b: u'簿', 0x66aeca08: u'操',
    0x66c75713: u'躍', 0x66cd72fe: u'炉', 0x66d63a1c: u'違', 0x66ed2d5e: u'妄',
    0x672876ef: u'衝', 0x672d3200: u'舞', 0x678528be: u'拒', 0x679b78ca: u'朽',
    0x67a615d9: u'鼻', 0x68154f6f: u'像', 0x68195500: u'穏', 0x6857edd1: u'績',
    0x687dda33: u'君', 0x6888fe40: u'黙', 0x68d2cfaf: u'並', 0x690b740c: u'小',
    0x690c1d37: u'虹', 0x69800e2c: u'指', 0x69bab1c7: u'車', 0x69c61764: u'速',
    0x69d6c398: u'血', 0x6a229a39: u'裏', 0x6a69ac2b: u'脈', 0x6a740f69: u'六',
    0x6ad17af8: u'稼', 0x6af06caf: u'狼', 0x6af9cece: u'初', 0x6b02e584: u'奥',
    0x6b41a6c3: u'徒', 0x6b44e830: u'関', 0x6b56d358: u'邪', 0x6b6a0f51: u'等',
    0x6b70c650: u'戯', 0x6bb35853: u'仙', 0x6bc09d72: u'補', 0x6bff9178: u'到',
    0x6c3be4f2: u'響', 0x6c80be77: u'津', 0x6c8ac459: u'婚', 0x6cd4c9e0: u'未',
    0x6cded06a: u'悩', 0x6cf9966a: u'低', 0x6d7c118d: u'石', 0x6d9abe83: u'土',
    0x6e28ad49: u'紅', 0x6e2f889c: u'叉', 0x6ed7368a: u'気', 0x6ee71d6e: u'基',
    0x6eecee36: u'就', 0x6ef4b7d3: u'能', 0x6ff34654: u'八', 0x7002e4b2: u'脅',
    0x7021a344: u'爪', 0x705ca43f: u'畑', 0x70974a75: u'圏', 0x709f1709: u'警',
    0x70b8aa30: u'序', 0x70ebc2c1: u'蘇', 0x710d6b00: u'隠', 0x713576b4: u'窪',
    0x71af2041: u'千', 0x71b85b00: u'発', 0x71bff0aa: u'腰', 0x71dc6cd3: u'閉',
    0x72005c7f: u'映', 0x72145fe7: u'窟', 0x72693550: u'替', 0x7275cfa0: u'給',
    0x72b7dbd7: u'黒', 0x72c78ca2: u'与', 0x739df19e: u'豪', 0x73cb0007: u'姫',
    0x73d0b8f3: u'塚', 0x73dad3f7: u'為', 0x749fb842: u'客', 0x74a8d809: u'緩',
    0x74c305d2: u'攻', 0x74ce5c2d: u'療', 0x754d7936: u'侵', 0x75b7d548: u'底',
    0x76079bd0: u'充', 0x762e1a50: u'鋼', 0x7649c0c4: u'尊', 0x765bf3e5: u'刺',
    0x76a573b2: u'臓', 0x76bdf59c: u'率', 0x76dbb9b9: u'泉', 0x7704ab1d: u'卿',
    0x770c0aa4: u'他', 0x7716f468: u'件', 0x776f754f: u'凍', 0x779f6324: u'良',
    0x77b87db2: u'推', 0x7856c720: u'蛇', 0x785938d7: u'床', 0x786f07ec: u'張',
    0x78a6152f: u'連', 0x78a8637b: u'人', 0x78ae3d8e: u'鳴', 0x79816469: u'去',
    0x79df9a37: u'逮', 0x79e75afa: u'摂', 0x7a012db1: u'堀', 0x7a0cdfc1: u'衛',
    0x7a2bf0bb: u'揺', 0x7a3fc39f: u'日', 0x7a5b38fc: u'眠', 0x7a5d32fd: u'割',
    0x7acaf5b5: u'篭', 0x7ae27a9f: u'担', 0x7ae6d619: u'慄', 0x7b8645e6: u'女',
    0x7b9c82c9: u'参', 0x7bbf7816: u'遥', 0x7be9f349: u'波', 0x7c5e8650: u'樹',
    0x7c83a84e: u'呪', 0x7ca46b99: u'海', 0x7cc8289d: u'含', 0x7cd00aa7: u'間',
    0x7cdfff20: u'曲', 0x7d1b3ad7: u'救', 0x7d67235d: u'益', 0x7d8ecf9c: u'希',
    0x7d94a682: u'棺', 0x7d9d7468: u'馬', 0x7dc2e79f: u'元', 0x7de74160: u'品',
    0x7e0614cb: u'養', 0x7e28db0b: u'描', 0x7e2b6042: u'表', 0x7e2ba1ad: u'漁',
    0x7e681a85: u'惨', 0x7e73467b: u'俊', 0x7e9d3fc2: u'様', 0x7ed7b535: u'賞',
    0x7f083f92: u'搭', 0x7f14e6a4: u'星', 0x7f2c3fb3: u'荷', 0x7f8a60ce: u'備',
    0x7f9c8624: u'万', 0x7fbe2bfb: u'肉', 0x801df9dc: u'冒', 0x804874f1: u'律',
    0x807afb54: u'派', 0x80e55938: u'紫', 0x8116f31c: u'適', 0x818785c6: u'承',
    0x81dbbc4c: u'脚', 0x8207574e: u'潮', 0x82477abc: u'決', 0x827e7e7f: u'背',
    0x8297c82f: u'挑', 0x8319da42: u'灯', 0x837e8f21: u'平', 0x83b7c278: u'礼',
    0x83f1ba66: u'懸', 0x84112685: u'巡', 0x841b08e2: u'更', 0x84215d17: u'鈴',
    0x848bd887: u'傾', 0x849ad71a: u'齢', 0x849f5d6b: u'圧', 0x84b6ebde: u'怨',
    0x84dafdc8: u'忙', 0x84db00b9: u'箇', 0x84e4daa6: u'高', 0x85400e72: u'糸',
    0x85df7dab: u'栄', 0x85ee2f92: u'酬', 0x8615b07c: u'木', 0x861cc27a: u'博',
    0x863241f8: u'損', 0x8668007f: u'板', 0x866e995b: u'逐', 0x86eff93a: u'即',
    0x8761e34c: u'匠', 0x87694454: u'興', 0x87848b80: u'退', 0x87f4e1a4: u'戦',
    0x87f91d31: u'立', 0x8818c4cd: u'浜', 0x881bb053: u'申', 0x882cf83a: u'示',
    0x883f4efa: u'功', 0x886c4954: u'東', 0x88854560: u'劫', 0x88a22059: u'母',
    0x88b3423d: u'常', 0x88dae28f: u'悔', 0x893e07b2: u'和', 0x89a0c10a: u'北',
    0x8a00d3ee: u'動', 0x8a185c4a: u'肝', 0x8a704fe9: u'嫉', 0x8a73b494: u'呼',
    0x8a95c959: u'寝', 0x8aad599f: u'社', 0x8ad1a500: u'協', 0x8b027c69: u'貸',
    0x8b293062: u'寂', 0x8b758aae: u'引', 0x8bad3dec: u'育', 0x8bcae185: u'修',
    0x8bec300a: u'徴', 0x8bf9f393: u'巨', 0x8c05044d: u'撒', 0x8c1df2c9: u'役',
    0x8c3ed2cf: u'幹', 0x8c5f8ec7: u'孝', 0x8c9813a2: u'篤', 0x8ca0c50a: u'活',
    0x8d44843e: u'諸', 0x8d5d6621: u'判', 0x8da376b5: u'称', 0x8df22ac3: u'施',
    0x8e1a7ade: u'瞬', 0x8e36aab5: u'粒', 0x8e4364cc: u'暗', 0x8e46cf06: u'証',
    0x8e6af47b: u'誇', 0x8eed74a7: u'量', 0x8f26bff7: u'営', 0x8f6a4b29: u'応',
    0x8f9a75c7: u'般', 0x900b319c: u'身', 0x90122902: u'印', 0x9027842e: u'術',
    0x9031a7b8: u'裕', 0x903ebf58: u'音', 0x90512948: u'獣', 0x9080022b: u'英',
    0x90827f65: u'架', 0x909785db: u'売', 0x909a7ee3: u'杉', 0x90a44d91: u'唄',
    0x90c64f69: u'酒', 0x91032405: u'別', 0x914a9d5f: u'還', 0x91675764: u'藤',
    0x917f18a2: u'辱', 0x91d37b8c: u'宇', 0x91f70191: u'狭', 0x922b4891: u'風',
    0x9235e51b: u'戒', 0x92753ca6: u'卑', 0x92acf13d: u'杖', 0x92d69b42: u'登',
    0x92ef2698: u'軽', 0x9323fd34: u'繁', 0x934467c6: u'互', 0x9384f1be: u'漂',
    0x939e135a: u'拝', 0x93a7aa60: u'招', 0x93dad5b5: u'淡', 0x9406026f: u'頓',
    0x940833ef: u'儀', 0x94b47e71: u'厨', 0x94b6e13e: u'族', 0x94d3f62b: u'犬',
    0x94d5a7fa: u'忘', 0x94e7c71e: u'部', 0x950b468f: u'教', 0x95484ef1: u'吐',
    0x95c99644: u'提', 0x95cb9cab: u'受', 0x964055b1: u'焦', 0x9653207e: u'段',
    0x9655e196: u'裂', 0x9672ebab: u'愛', 0x96bea4ef: u'駆', 0x96ea5d60: u'費',
    0x9727284b: u'掌', 0x977fbd41: u'言', 0x97b3ad05: u'敬', 0x97d539b7: u'左',
    0x97d641ec: u'盗', 0x97decb03: u'案', 0x980b501c: u'堕', 0x981f0c3e: u'徹',
    0x98b6487a: u'願', 0x98b980ee: u'緑', 0x98e4a4ec: u'進', 0x9940421f: u'奴',
    0x9941ee83: u'賑', 0x99944d94: u'予', 0x999e61ed: u'束', 0x99b3891a: u'計',
    0x99dfba0c: u'吹', 0x9a0d7cec: u'炎', 0x9a2b1585: u'居', 0x9a34012d: u'妻',
    0x9a4ad779: u'閃', 0x9ac4c82a: u'刑', 0x9adba9af: u'月', 0x9b3bb5b2: u'覧',
    0x9b3cc8d0: u'優', 0x9b566f96: u'糧', 0x9b763fc7: u'題', 0x9b8ef002: u'影',
    0x9bb1d467: u'陥', 0x9bb65fc3: u'康', 0x9bdf159b: u'忠', 0x9bf90db3: u'名',
    0x9c493609: u'豆', 0x9c910c1f: u'道', 0x9d184ef1: u'資', 0x9d6aa281: u'確',
    0x9d965c1a: u'外', 0x9e09f33f: u'祝', 0x9e0a567a: u'討', 0x9e37d02e: u'肩',
    0x9e55b5a6: u'骨', 0x9e617fb5: u'書', 0x9e657375: u'隔', 0x9ebd177b: u'及',
    0x9eca8e89: u'的', 0x9ecd4ade: u'粉', 0x9f69c1d5: u'保', 0x9f6dc7cb: u'免',
    0x9f8c464d: u'導', 0x9ff1defc: u'反', 0xa0393d04: u'性', 0xa03a4b24: u'用',
    0xa057ef9d: u'締', 0xa080b132: u'百', 0xa0a5494d: u'番', 0xa12beb6d: u'浄',
    0xa1472660: u'雌', 0xa15ce83a: u'町', 0xa182a578: u'紙', 0xa25d9adb: u'灼',
    0xa322e5af: u'工', 0xa34913ca: u'形', 0xa3b996a2: u'村', 0xa3f29830: u'恥',
    0xa4cc49da: u'貧', 0xa4db3e18: u'誓', 0xa580cfdc: u'詮', 0xa58498df: u'酷',
    0xa5ddabdc: u'悲', 0xa68995b3: u'溜', 0xa6caf850: u'宙', 0xa6dd850f: u'超',
    0xa6ea3945: u'劣', 0xa7025944: u'力', 0xa7084840: u'軟', 0xa70b37f4: u'雪',
    0xa724b72c: u'線', 0xa73589b4: u'腕', 0xa79a60cd: u'干', 0xa81706da: u'輪',
    0xa8aad0d9: u'谷', 0xa8d6af8a: u'恋', 0xa900496c: u'存', 0xa91653c2: u'型',
    0xa9275ad3: u'巻', 0xa94db376: u'励', 0xa961b909: u'手', 0xa9d3a61e: u'詳',
    0xa9fdd163: u'通', 0xaa297abf: u'聞', 0xaa78cfc2: u'疫', 0xaa8d5246: u'覆',
    0xaa9aba87: u'陣', 0xaaa6eec3: u'心', 0xaaaa7f95: u'夷', 0xaab91dc8: u'怖',
    0xaaba1b11: u'尾', 0xabc9fce5: u'渋', 0xabf51dd1: u'抵', 0xabf7c3df: u'声',
    0xac2398dc: u'混', 0xac31e1dc: u'国', 0xac4f10dc: u'遅', 0xac5d8541: u'棄',
    0xac6bd2fb: u'球', 0xac7a9355: u'歌', 0xacb06d58: u'巫', 0xacd197fa: u'非',
    0xad358f9a: u'悠', 0xad44d16f: u'志', 0xad63f7ed: u'誉', 0xad704347: u'眼',
    0xadc6224d: u'掛', 0xade31123: u'郎', 0xae10163a: u'鎮', 0xae2035f5: u'原',
    0xae3cc810: u'善', 0xae91c38f: u'絶', 0xaea082db: u'趣', 0xaea58bba: u'敵',
    0xaef933ef: u'掲', 0xaefe9539: u'虎', 0xaf0c0561: u'易', 0xaf391da7: u'比',
    0xaf40e336: u'択', 0xaf49b33b: u'経', 0xaf503715: u'達', 0xaf8f0a53: u'司',
    0xafa84df7: u'属', 0xafc77d8e: u'複', 0xb001f1c8: u'列', 0xb025e410: u'評',
    0xb03c89cf: u'首', 0xb05c7655: u'朝', 0xb05fafdb: u'対', 0xb0dfce0d: u'催',
    0xb1762a55: u'格', 0xb1ca443c: u'郷', 0xb2319f7c: u'過', 0xb2338e14: u'校',
    0xb237ce1f: u'汚', 0xb2889c83: u'地', 0xb297d0f9: u'正', 0xb2b59f0e: u'境',
    0xb2d1182f: u'縄', 0xb2ddf8e5: u'述', 0xb2f2841a: u'里', 0xb2f64dc5: u'獲',
    0xb2f8f8b2: u'物', 0xb323b917: u'慢', 0xb334aa2c: u'行', 0xb34fb0fa: u'携',
    0xb3a3f6b3: u'巣', 0xb3b14d3b: u'魔', 0xb3e0dc73: u'授', 0xb43dfe28: u'枠',
    0xb4ac13f0: u'上', 0xb4b80245: u'哲', 0xb560c04c: u'師', 0xb57e9407: u'頂',
    0xb5b85b6f: u'円', 0xb5d641a5: u'致', 0xb5ded380: u'仇', 0xb62ef02b: u'牙',
    0xb646ba10: u'帳', 0xb70c2bda: u'材', 0xb70d517c: u'昇', 0xb7717af5: u'息',
    0xb792c712: u'義', 0xb7b6f4c3: u'倍', 0xb7c93216: u'民', 0xb7d3089e: u'勲',
    0xb7dda09e: u'昼', 0xb7f87984: u'墜', 0xb87e8bbc: u'安', 0xb8a850ef: u'再',
    0xb9056322: u'一', 0xb90c251f: u'也', 0xb993f1b8: u'南', 0xb9a15e40: u'料',
    0xb9b5035e: u'晶', 0xb9bbfb40: u'水', 0xb9c7dafb: u'雰', 0xb9ea56d9: u'角',
    0xba1536a7: u'年', 0xba241fa0: u'殖', 0xba298bb1: u'軍', 0xba3234ae: u'督',
    0xba5406fd: u'耐', 0xba624ecb: u'獄', 0xbb31bc79: u'層', 0xbb4eb845: u'例',
    0xbb6e78af: u'源', 0xbb91a838: u'伸', 0xbb9c7f52: u'共', 0xbb9ca2c8: u'増',
    0xbbcf9ebc: u'識', 0xbbe73874: u'果', 0xbc319840: u'片', 0xbcfb8f40: u'額',
    0xbd2c986b: u'焼', 0xbd4aa3a8: u'翔', 0xbd54ccfa: u'夜', 0xbe290ede: u'納',
    0xbe5b27ed: u'謎', 0xbe6e184e: u'錯', 0xbe7a57e0: u'監', 0xbeafe572: u'曇',
    0xbedd481c: u'歯', 0xbf487c06: u'係', 0xbfba90bf: u'詩', 0xc0115be3: u'真',
    0xc040e8a2: u'川', 0xc05b1594: u'激', 0xc0720d7c: u'旋', 0xc08e3fbb: u'捧',
    0xc0a89425: u'程', 0xc0fc5464: u'状', 0xc10a4ae2: u'節', 0xc12278d8: u'抜',
    0xc207350c: u'瀬', 0xc20aa75d: u'糸', 0xc21f55c1: u'偏', 0xc233ed5c: u'旅',
    0xc2781251: u'画', 0xc2c71ce3: u'延', 0xc2fb7862: u'制', 0xc3744385: u'読',
    0xc3748d04: u'刃', 0xc405f098: u'側', 0xc44870f5: u'尻', 0xc46c1342: u'唯',
    0xc4a4455d: u'敗', 0xc4bc833e: u'傑', 0xc5448dc7: u'由', 0xc59ad332: u'買',
    0xc5ffaf24: u'粋', 0xc62ca35c: u'老', 0xc6c78491: u'知', 0xc6d64e18: u'録',
    0xc6ef74ee: u'患', 0xc6f5b2df: u'金', 0xc6f8b679: u'草', 0xc7101547: u'選',
    0xc74bc7cd: u'幸', 0xc75914c0: u'任', 0xc7809eb5: u'揮', 0xc7d7bc88: u'彦',
    0xc7fd14b9: u'止', 0xc8134c24: u'局', 0xc8165e58: u'路', 0xc852685f: u'健',
    0xc8b42418: u'挙', 0xc8e6d134: u'歴', 0xc94088e5: u'創', 0xca37cfac: u'調',
    0xca90aa14: u'洞', 0xcac368a6: u'玉', 0xcb49a1c2: u'食', 0xcb5c9440: u'胸',
    0xcb6972db: u'膨', 0xcb8127f9: u'市', 0xcbd9fb48: u'偽', 0xcbe35f00: u'疾',
    0xcc6a3002: u'森', 0xcc7f6744: u'幻', 0xcc8b4f7e: u'賃', 0xcc9b64ed: u'飲',
    0xcca05bb5: u'薬', 0xccb13f61: u'望', 0xccc2855e: u'逆', 0xccdccec2: u'控',
    0xcd16afe2: u'情', 0xcd197778: u'助', 0xcd3a138c: u'観', 0xcd7806a7: u'贈',
    0xcdb8421f: u'剣', 0xcdc82d53: u'菊', 0xcdd8cd35: u'官', 0xcdf5c2c7: u'兼',
    0xce013709: u'投', 0xce2741f3: u'右', 0xce3f0b41: u'鈍', 0xce5577ed: u'烈',
    0xce9a3e80: u'快', 0xcf175d9d: u'酔', 0xcf20a85a: u'明', 0xcf7769fd: u'生',
    0xcf83fb70: u'実', 0xd0079142: u'避', 0xd01fa05e: u'喜', 0xd024944d: u'領',
    0xd04b447a: u'会', 0xd0eb1cbe: u'足', 0xd0eeeb1d: u'枚', 0xd110b6e8: u'照',
    0xd1385e2a: u'雷', 0xd14ea632: u'襲', 0xd1908202: u'憶', 0xd1dac94c: u'園',
    0xd1dd4785: u'処', 0xd1ddfc91: u'札', 0xd1fa0b93: u'叙', 0xd22292d0: u'惑',
    0xd236c277: u'狩', 0xd271ffc9: u'浮', 0xd2dce1e0: u'跡', 0xd2fcfe7e: u'総',
    0xd324983e: u'第', 0xd36a3c99: u'遂', 0xd383436b: u'瞳', 0xd390fe73: u'俺',
    0xd3de864e: u'殿', 0xd3df7029: u'従', 0xd45d0f1d: u'距', 0xd467c029: u'悟',
    0xd4adf928: u'支', 0xd4c385b0: u'親', 0xd4c9270f: u'奇', 0xd4dd9214: u'豊',
    0xd5062f1b: u'借', 0xd51bd7f1: u'主', 0xd526325a: u'面', 0xd5448d7c: u'異',
    0xd5528a34: u'渡', 0xd59436e1: u'写', 0xd5a76a33: u'版', 0xd5e6fb16: u'要',
    0xd610c1dc: u'誕', 0xd63baec5: u'慕', 0xd67b9947: u'赤', 0xd69e0cfb: u'密',
    0xd763c610: u'留', 0xd7b21846: u'談', 0xd7bc6ac7: u'勢', 0xd7e2fc62: u'脱',
    0xd7f961b1: u'媒', 0xd7ffc4d0: u'被', 0xd814c60e: u'砲', 0xd8298a4e: u'珍',
    0xd83d99c4: u'不', 0xd844eb5d: u'胞', 0xd8692cd1: u'青', 0xd88fb9c0: u'叩',
    0xd8ec66dc: u'罪', 0xd91b2c53: u'妨', 0xd956bdda: u'想', 0xd9abc4df: u'絵',
    0xd9e34ab9: u'槍', 0xda4d30ec: u'塔', 0xda639979: u'訪', 0xda9b3625: u'接',
    0xdb26df7f: u'文', 0xdb2c9450: u'謝', 0xdb5947f1: u'孤', 0xdb80fd98: u'向',
    0xdbab7c1a: u'覚', 0xdbed7436: u'拾', 0xdbf2e17d: u'詞', 0xdc46e35c: u'秀',
    0xdceb6a72: u'雲', 0xdcef4e28: u'視', 0xdd70cdb8: u'翌', 0xdd808361: u'卒',
    0xde1ed738: u'虚', 0xde5b25c7: u'愚', 0xde79b771: u'闇', 0xde8ce6ca: u'介',
    0xdec15e9f: u'武', 0xdeef44ea: u'場', 0xdf82e67e: u'見', 0xdfbeb5f4: u'末',
    0xdfec7614: u'熱', 0xdff47b8a: u'児', 0xe0016675: u'岸', 0xe00d8245: u'古',
    0xe06c34a5: u'当', 0xe06c66c0: u'光', 0xe07ad703: u'務', 0xe08202a0: u'思',
    0xe0839df9: u'入', 0xe0b626f7: u'多', 0xe1059c6c: u'態', 0xe140cd08: u'放',
    0xe17ae48c: u'精', 0xe1801129: u'断', 0xe1fbc123: u'始', 0xe24fed73: u'忌',
    0xe29ec902: u'美', 0xe2e06fb6: u'織', 0xe2e4436a: u'置', 0xe30f1098: u'陛',
    0xe32679ba: u'端', 0xe355a2d5: u'押', 0xe399f0e3: u'駄', 0xe3d2fda0: u'芸',
    0xe3ea458c: u'早', 0xe422e767: u'翼', 0xe432e6de: u'時', 0xe4540430: u'摘',
    0xe456ff00: u'賊', 0xe516fbe9: u'魚', 0xe538447c: u'骸', 0xe56c5706: u'載',
    0xe59bbf63: u'壁', 0xe5e2915a: u'深', 0xe5f06a66: u'飛', 0xe6066355: u'棒',
    0xe6329c3c: u'回', 0xe6476ac2: u'告', 0xe649127b: u'色', 0xe656371a: u'沖',
    0xe6a27c92: u'弾', 0xe6a6a622: u'打', 0xe6b3b7f5: u'現', 0xe6d3352e: u'値',
    0xe6fec4b1: u'飾', 0xe70b7193: u'鳩', 0xe7165eca: u'働', 0xe731d424: u'来',
    0xe740236a: u'握', 0xe7474a3b: u'静', 0xe79f6c2f: u'感', 0xe819ba0a: u'乱',
    0xe81c3627: u'秘', 0xe83558fb: u'彰', 0xe8410d77: u'類', 0xe8529a6f: u'縦',
    0xe86378cb: u'治', 0xe86b8771: u'周', 0xe8a42809: u'倒', 0xe8b06efb: u'獅',
    0xe8c5aaef: u'淵', 0xe8d8278d: u'街', 0xe8dc1bc2: u'忍', 0xe8e057f5: u'服',
    0xe9102709: u'項', 0xe9839103: u'犯', 0xe987cd30: u'屋', 0xea074080: u'賢',
    0xea399cb3: u'許', 0xea74a7c5: u'困', 0xeab96d2a: u'空', 0xeacd6654: u'付',
    0xeb046dcc: u'詠', 0xeb6f6d46: u'誘', 0xeb70f246: u'滋', 0xebcc1e6a: u'銭',
    0xec0ecee4: u'減', 0xec3e7a85: u'好', 0xec4f13dd: u'解', 0xec625fd9: u'暮',
    0xec829e76: u'策', 0xec95f42c: u'遇', 0xedc1013c: u'答', 0xedc335eb: u'孫',
    0xee025c46: u'流', 0xee1a450a: u'事', 0xee1e2342: u'域', 0xee1f2d61: u'三',
    0xee343277: u'化', 0xee7dc55f: u'壺', 0xee8d99d7: u'子', 0xeec7ad68: u'装',
    0xef63c309: u'縁', 0xef74d676: u'弘', 0xef791121: u'広', 0xefb17db5: u'横',
    0xeff7fc37: u'堂', 0xf0526ea4: u'布', 0xf05fddac: u'勇', 0xf075c4cd: u'祭',
    0xf0cfb4ba: u'港', 0xf0eb3ec1: u'因', 0xf1165983: u'却', 0xf12ed97b: u'電',
    0xf14ace6c: u'伴', 0xf1580148: u'契', 0xf16a5759: u'穴', 0xf197043b: u'維',
    0xf1a64c7c: u'今', 0xf22a5b8d: u'毛', 0xf23efee0: u'価', 0xf24067c5: u'権',
    0xf26564bb: u'塞', 0xf26cdfd0: u'者', 0xf2913265: u'怒', 0xf29c4531: u'竜',
    0xf2a5d6e6: u'少', 0xf2ba8a88: u'柔', 0xf2c8d58f: u'念', 0xf32080f2: u'菜',
    0xf39c6701: u'崇', 0xf3c2667c: u'皆', 0xf409674e: u'愉', 0xf421da99: u'相',
    0xf464e777: u'寛', 0xf496504b: u'頃', 0xf4d7d543: u'供', 0xf4e87895: u'何',
    0xf4f1bdea: u'募', 0xf4f9b232: u'祖', 0xf51a988a: u'築', 0xf51d346b: u'兄',
    0xf5287995: u'約', 0xf52ae1a0: u'可', 0xf5357e9a: u'矢', 0xf53a83fd: u'幅',
    0xf54d9d71: u'盤', 0xf586172a: u'虫', 0xf5976a90: u'研', 0xf5b7c4dc: u'恩',
    0xf5ba7986: u'敷', 0xf6173fa4: u'嫁', 0xf6285672: u'否', 0xf660ff3e: u'闘',
    0xf69e4363: u'論', 0xf69eaee6: u'振', 0xf6a39c1b: u'省', 0xf6b58a6a: u'禁',
    0xf701609e: u'政', 0xf70e68f6: u'寒', 0xf7116934: u'標', 0xf7347ad5: u'財',
    0xf78004ec: u'縛', 0xf7c8c646: u'恵', 0xf7e400a9: u'雑', 0xf81ca800: u'嘆',
    0xf85519e9: u'疲', 0xf866b22b: u'展', 0xf8904976: u'鍛', 0xf9200405: u'負',
    0xf9a8bc46: u'笛', 0xf9f51489: u'探', 0xf9fc845a: u'害', 0xfa128ff5: u'起',
    0xfa1dc499: u'柱', 0xfa889186: u'目', 0xfa9e58cb: u'内', 0xfaa16130: u'峡',
    0xfaae7f3c: u'依', 0xfab5699e: u'罰', 0xfabad410: u'踏', 0xfaea19a0: u'才',
    0xfaf259fa: u'恐', 0xfb0521f5: u'待', 0xfb76e252: u'跳', 0xfb984160: u'悪',
    0xfbc75443: u'口', 0xfbc8313c: u'環', 0xfc0b166e: u'査', 0xfc101580: u'肖',
    0xfc13685c: u'丈', 0xfc20ba11: u'庭', 0xfc4a036f: u'橋', 0xfc69c6ba: u'威',
    0xfc8066df: u'薄', 0xfc948b8a: u'仲', 0xfc9757a5: u'戸', 0xfcb14e34: u'暴',
    0xfcd610fc: u'屈', 0xfd343808: u'検', 0xfd48c0b2: u'貴', 0xfd5a2c11: u'家',
    0xfd7a6767: u'酸', 0xfdc1749a: u'越', 0xfde73278: u'砕', 0xfde7a419: u'痛',
    0xfe3f9189: u'守', 0xfe619e63: u'毎', 0xfeed4f99: u'頼', 0xff6a0f30: u'秩',
    0xff7e8a44: u'叱', 0xffb8ebec: u'落', 0xffe98fb1: u'双',
}


# Decode text from the Japanese game version.
def decodeJP(data, kanjiBitmap):
    text = u""

    largeFont = False

    dataSize = len(data)

    i = 0
    while i < dataSize:
        c = ord(data[i])
        i += 1

        if c == 0x00:

            # End of string
            break

        elif c > 0x00 and c <= 0x1f:

            # Control code
            code, i = decodeControl(c, data, i)
            text += code

            if c == 0x14:
                largeFont = True
            elif c == 0x0e:
                largeFont = False

        elif c >= 0x28 and c <= 0x7a:

            # Hiragana
            sjis = '\x82' + chr(c + 0x77)
            text += sjis.decode("sjis")

        elif c >= 0x81 and c <= 0x84:

            # SJIS double-byte code
            sjis = chr(c) + data[i]
            i += 1
            text += sjis.decode("sjis")

        elif (c >= 0x88 and c <= 0x9f):

            # Kanji
            c2 = ord(data[i])
            i += 1

            found = False

            if largeFont:

                # The large (PSX ROM) font uses standard SJIS encoding
                sjis = chr(c) + chr(c2)
                text += sjis.decode("sjis")
                found = True

            elif kanjiBitmap is None:

                # Look up in global Kanji list
                if c == 0x88:
                    text += kanji1[c2 - 1]
                    found = True
                elif c == 0x89:
                    text += kanji2[c2 - 1]
                    found = True

            else:

                # Map-specific Kanji, look up via a hash of the character image
                offset = ((c - 0x88) * 0xfd + c2 - 1) * 22

                if offset <= len(kanjiBitmap) - 22:
                    hash = zlib.crc32(str(kanjiBitmap[offset:offset + 22])) & 0xffffffff

                    try:
                        text += kanjiByHash[hash]
                        found = True
                    except KeyError:
                        print "Unknown Kanji %02x %02x" % (c, c2)
                        print "Hash = 0x%08x" % hash
                        for y in xrange(11):
                            v = (kanjiBitmap[offset + y*2] << 8) | kanjiBitmap[offset + y*2 + 1]
                            s = ""
                            for x in xrange(16):
                                if v & 0x8000:
                                    s += "#"
                                else:
                                    s += "."
                                v <<= 1
                            print s
                        print

            if not found:
                text += u'{KANJI %02x %02x}' % (c, c2)

        elif c >= 0xa7 and c <= 0xdd:

            # Katakana
            text += katakana[c - 0xa7]

        else:

            # Unknown
            text += u'{' + hex(c) + u'}'

    return text


# International character set (variation of DOS code page 437)
#
# Note: The characters ÁÍÚ are from code page 850 and are used in the
# Spanish release although they are not actually present in the game's
# font.
origCharset = (
    u" !\"#$%&'()*+,-./"  # 20..2f
    u"0123456789:★<=>?"   # 30..3f
    u"「ABCDEFGHIJKLMNO"  # 40..4f
    u"PQRSTUVWXYZ[♂]』_"  # 50..5f
    u"`abcdefghijklmno"   # 60..6f
    u"pqrstuvwxyz{♀}『 "  # 70..7f
    u"ÇüéâäàåçêëèïîìÄÅ"   # 80..8f
    u"ÉæÆôöòûùÿÖÜ¢£¥▯ƒ"   # 90..9f
    u"áíóúñÑªº¿▯¬½¼¡«»"   # a0..af
    u"▯▯▯▯▯Á▯▯▯▯▯▯▯▯▯▯"   # b0..bf
    u"▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯"   # c0..cf
    u"▯▯▯▯▯▯Í▯▯▯▯▯▯▯▯▯"   # d0..df
    u"▯ß▯¶▯▯µ▯▯Ú▯▯▯▯▯▯"   # e0..ef
    u"▯±▯▯▯▯÷▯°∙▯▯▯▯▯▯"   # f0..ff
)

# Alternative character set (variation of DOS code page 850), designed for
# use with a custom font
altCharset = (
    u" !\"#$%&'()*+,-./"  # 20..2f
    u"0123456789:★<=>?"   # 30..3f
    u"“ABCDEFGHIJKLMNO"   # 40..4f
    u"PQRSTUVWXYZ[♂]’_"   # 50..5f
    u"”abcdefghijklmno"   # 60..6f
    u"pqrstuvwxyz{♀}‘ "   # 70..7f
    u"ÇüéâäàåçêëèïîìÄÅ"   # 80..8f
    u"ÉæÆôöòûùÿÖÜø£Ø▯ƒ"   # 90..9f
    u"áíóúñÑªº¿▯~½¼¡«»"   # a0..af
    u"▯▯▯▯▯ÁÂÀ▯▯▯▯▯▯▯▯"   # b0..bf
    u"▯▯▯▯▯▯ãÃ▯▯▯▯▯▯▯▯"   # c0..cf
    u"ðÐÊËÈ▯ÍÎÏ▯▯▯▯▯Ì▯"   # d0..df
    u"ÓßÔÒõÕµþÞÚÛÙýÝœŒ"   # e0..ef
    u"▯±…▯▯▯÷▯°∙▯▯▯▯▯▯"   # f0..ff
)

charset = origCharset

def setAltCharset():
    global charset
    charset = altCharset

# Characters which must be escaped when decoding
escapeChars = u"\\{}"


# Decode text from the US or European game version.
def decodeINT(data):
    text = u""

    dataSize = len(data)

    i = 0
    while i < dataSize:
        c = ord(data[i])
        i += 1

        if c == 0x00:

            # End of string
            break

        elif c > 0x00 and c <= 0x1f:

            # Control code
            code, i = decodeControl(c, data, i)

            text += code

        else:

            # Regular character (note: only the EU versions use characters >= 0x80;
            # the US version uses 7-bit ASCII, with some exceptions)
            t = charset[c - 0x20]

            if t in escapeChars:
                text += u"\\"

            text += t

    return text


# Decode Wild Arms text string to unicode string.
def decode(data, version, kanjiBitmap = None):
    if isJapanese(version):
        return decodeJP(data, kanjiBitmap)
    else:
        return decodeINT(data)


# Encode unicode string to Wild Arms text string.
def encode(text, version):
    if isJapanese(version):
        raise EnvironmentError, "Japanese text encoding is not supported"

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
                data += chr(charset.index(c) + 0x20)
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

            # Find the command code
            try:
                code = codeOfCommand[keyword]
            except KeyError:
                raise ValueError, "Unknown command '%s' in string '%s'" % (keyword, text)

            data += chr(code)


            # Get the argument
            arg = None
            argLen = controlCodes[code][0]

            if argLen:
                m = re.match(keyword + r" (\d+)", command)
                arg = int(m.group(1))
            else:
                m = re.match(keyword, command)

            if not m:
                raise ValueError, "Syntax error in command '%s' in string '%s'" % (command, text)

            if argLen:
                if arg < 0 or arg >= 10**argLen:
                    raise "Argument of %s command out of range in string '%s'" % (keyword, text)

                data += ("%%0%dd" % argLen) % arg

        else:

            # Regular printable character
            try:
                t = charset.index(c) + 0x20
                data += chr(t)

                if (version == Version.US) and (t >= 0x80):
                    raise ValueError

            except ValueError:
                raise ValueError, "Unencodable character '%s' in string '%s'" % (c, text)

    # Terminate string
    return data + '\0'
