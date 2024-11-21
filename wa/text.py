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

from .version import Version, isJapanese


# Text control codes
controlCodes = [

    # (argLen, code)
    (0, "0x00"),
    (1, "STR"),       # 0x01 xx       - string parameter
    (1, "NUM"),       # 0x02 xx       - signed numeric parameter
    (1, "UNUM"),      # 0x03 xx       - unsigned numeric parameter
    (1, "HEX"),       # 0x04 xx       - hexadecimal parameter
    (1, "CHAR"),      # 0x05 xx       - character name
    (1, "ITEM"),      # 0x06 xx       - item name
    (1, "SPELL"),     # 0x07 xx       - spell name
    (1, "ITEMICON"),  # 0x08 xx       - item icon
    (1, "SPELLICON"), # 0x09 xx       - spell icon
    (1, "TOOL"),      # 0x0a xx       - tool name
    (1, "TOOLICON"),  # 0x0b xx       - tool icon
    (0, "CLEAR"),     # 0x09          - clear window
    (0, "CR"),        # 0x0d          - new line
    (0, "SMALL"),     # 0x0e          - switch to regular small (12x12) font (JP only)
    (0, "SCROLL"),    # 0x0f          - scroll up 1 line
    (0, "PAUSE"),     # 0x10          - pause until OK button is pressed
    (1, "COLOR"),     # 0x11 xx       - set text color
    (3, "SOUND"),     # 0x12 xx xx xx - play sound effect
    (0, "NOP"),       # 0x13          - nop
    (0, "LARGE"),     # 0x14          - switch to large (16x16) font (JP only)
    (2, "SPEED"),     # 0x15 xx xx    - set text speed
    (2, "WAIT"),      # 0x16 xx xx    - wait xxxx frames
    (0, "CONTINUE"),  # 0x17          - continue automatically after message (don't pause)
    (0, "XSHADOW"),   # 0x18          - toggle text shadow in X direction
    (0, "YSHADOW"),   # 0x19          - toggle text shadow in Y direction
    (1, "ASK"),       # 0x1a xx       - ask question
    (0, "ASYNC"),     # 0x1b          - continue script while message is being displayed
    (0, "0x1c"),
    (0, "0x1d"),
    (0, "0x1e"),
    (0, "0x1f"),
]

# Inverse mapping of commands to control codes
codeOfCommand = {controlCodes[i][1]:i for i in range(len(controlCodes))}


# Decode text control code, returning a (code, new_index) tuple.
def decodeControl(c, data, index):
    argLen, code = controlCodes[c]

    arg = data[index:index + argLen]

    if argLen > 0:
        code = code + ' ' + arg.decode("ascii")

    return ('{' + code + '}', index + argLen)


# Katakana table (like Shift-JIS but full-width)
katakana = (
    "ァィゥェォャュョッーアイウエオカ"  # a7..b6
    "キクケコサシスセソタチツテトナニ"  # b7..c6
    "ヌネノハヒフヘホマミムメモヤユヨ"  # c7..d6
    "ラリルレロワン"                    # d7..dd
)

# Kanji table bank 1 (88 xx)
kanji1 = (
      "持道具使各特殊装備武器防身戦闘時行動傾向指示状態任意変更回復味"  # 01..1f
    "方単体不能完全毒治療病気魔力封印混乱忘却異常冒険一中断者逮捕会員"  # 20..3f
    "証度町便利地図表出裏残弾数値補給早撃消費軽減法記録腕上昇反応加工"  # 40..5f
    "合鍵修得経験倍化右手用無効属性果通攻付与水火風雷心聖代歩前進確率"  # 60..7f
    "打避運伝説左書敵吸収頭部静炎花妻品失巨人善悪薬草古増幅置竜神像獅"  # 80..9f
    "子王女言葉本名仕強白石胸宝声紋登呼魂三種俺必帰込刻柱結界小型発射"  # a0..bf
    "拡散照連続精感式高焼夷携帯荷電粒砲空間作相転位兵同抜刀衝波物盗峰"  # c0..df
    "半分命後放切定剣宿解牙貫影技広範囲次元狭現換札山脈渡落下岩碑"      # e0..fd
)

# Kanji table bank 2 (89 xx)
kanji2 = (
      "謎試練壊機械浪士館授騎留思念超眠御抵抗還姿自除問入口戻調閉低霊"  # 01..1f
    "球止爆保護形訪瞬移去集様受在最大段守割替音楽整理頓何選択障害吹飛"  # 20..3f
    "探知速可繰的爪多目色秘暖光限計議話杖村院城港場船基房森塚憶遺跡棺"  # 40..5f
    "殿死迷宮号庭園海深淵堕天廊廃屋夢幻島祭壇雪峡谷別複写直活管画面終"  # 60..7f
    "了先容量削読逃隊列予枠内他旅少年敗制尽獲弱点取起着闇支援接生殺順"  # 80..9f
    "番決未烈閃暴周致禁呪文紫改危質急論象金粉実菌糸導我流字斬奥義凶刃"  # a0..bf
    "舞陣夜叉奇宇宙振怪線翼氷巻裂仲走潜覚醒詠唱"                        # c0..d4
)

# Mapping of Kanji bitmap hash (CRC32) to unicode
kanjiByHash = {
    0x0004e407: '住', 0x0040a586: '鼓', 0x008bd144: '鎧', 0x0121a417: '中',
    0x01ccd1a4: '令', 0x0216cca9: '礎', 0x02385585: '届', 0x023c1223: '配',
    0x024aabe7: '慎', 0x027674a1: '爆', 0x02a05095: '篇', 0x02b82810: '妬',
    0x02bf5738: '準', 0x02dac8cc: '西', 0x02e54b3c: '労', 0x034d30ea: '重',
    0x0369ae46: '拠', 0x03855552: '荒', 0x040cbd14: '幽', 0x0430ce9e: '封',
    0x0443f560: '半', 0x0481aa67: '雄', 0x04a93452: '語', 0x04f8ad58: '霊',
    0x05038f66: '堅', 0x05442e2a: '削', 0x0549fe53: '謀', 0x055b5ce2: '夢',
    0x05950820: '詰', 0x059f9e11: '範', 0x05ac91e9: '野', 0x05c33cd6: '店',
    0x05e85590: '誠', 0x0617875a: '法', 0x0619a7ed: '妙', 0x0655a0c1: '七',
    0x065de255: '窓', 0x06bcac11: '習', 0x06e62626: '芽', 0x0713f98d: '二',
    0x0717bddf: '宏', 0x07321911: '滞', 0x0764b621: '帰', 0x07b6d7ec: '鎖',
    0x07e140ad: '歩', 0x07e1a1e6: '都', 0x07f589b5: '記', 0x0858a548: '冠',
    0x08822518: '埋', 0x0894b125: '滅', 0x089f914c: '独', 0x08c6690e: '泊',
    0x090bb6a3: '練', 0x0916b682: '析', 0x091f5aab: '問', 0x096928e3: '組',
    0x098c18f2: '徳', 0x0998fd60: '彼', 0x09a2f81d: '理', 0x09a93a8d: '渇',
    0x09c8fcf0: '勉', 0x09edb2f9: '期', 0x09f8867e: '弱', 0x09ff6c1d: '姿',
    0x0a6622c2: '浸', 0x0ad5c09a: '十', 0x0ae78b1e: '寸', 0x0b5446d8: '究',
    0x0bf3dec2: '統', 0x0c1405d1: '縮', 0x0c3984b0: '房', 0x0c3c8bd2: '迷',
    0x0c806bb5: '騒', 0x0c86586d: '寄', 0x0d2845a3: '頑', 0x0d3093b5: '匹',
    0x0d3c7ec8: '盛', 0x0db9f593: '降', 0x0dd34472: '図', 0x0e03297a: '方',
    0x0e31308b: '演', 0x0e51fa88: '玄', 0x0ef2244b: '射', 0x0f135d9b: '同',
    0x0f14795c: '微', 0x104c4b14: '柄', 0x109187ab: '集', 0x110e7582: '嬢',
    0x1127e974: '命', 0x11ba4826: '隊', 0x11da5e33: '迎', 0x11fc44e1: '転',
    0x1204d59e: '伯', 0x120df1c4: '歓', 0x1213a7f6: '富', 0x12373aa8: '整',
    0x1248d3d0: '臨', 0x12d0008c: '吸', 0x12e16534: '白', 0x12f6f127: '点',
    0x1311e686: '御', 0x13586d87: '求', 0x135b4ca6: '戻', 0x13965e25: '抱',
    0x139e92c3: '掘', 0x13a03724: '誤', 0x13d426a2: '新', 0x14087d76: '故',
    0x1412332b: '林', 0x14c85377: '訓', 0x150bcb42: '顔', 0x15491d83: '凶',
    0x155910ef: '数', 0x156035d2: '飯', 0x15b86c66: '収', 0x15ca2237: '破',
    0x15d45209: '略', 0x165067d5: '館', 0x1660603b: '騎', 0x16897c12: '永',
    0x16a60232: '崩', 0x16aab0fc: '了', 0x16e508c6: '固', 0x16f59e05: '試',
    0x171a8caf: '輩', 0x1739a61f: '限', 0x1762c681: '遊', 0x17badac7: '刀',
    0x17d426a5: '将', 0x17dcc040: '亀', 0x181ef792: '郊', 0x18351efd: '抹',
    0x18618a74: '娘', 0x18bf9770: '歪', 0x1928179d: '机', 0x192a3d52: '体',
    0x19d501c2: '徐', 0x19f2c6ee: '赴', 0x19f878c4: '軌', 0x19f9fdba: '缶',
    0x1a77c209: '死', 0x1a8d74a7: '太', 0x1aa14a13: '危', 0x1ac53bbc: '泣',
    0x1ac65897: '注', 0x1b005165: '機', 0x1b0a6278: '紹', 0x1b10c9a5: '特',
    0x1b298aec: '偉', 0x1b643a6e: '銀', 0x1b97e768: '則', 0x1be9536c: '魅',
    0x1c233a39: '史', 0x1c6879b4: '福', 0x1cafda57: '埒', 0x1d54c7fa: '両',
    0x1d72b957: '景', 0x1d97a6b2: '規', 0x1dac0764: '甲', 0x1e25ebad: '劇',
    0x1e371159: '冊', 0x1e4efd3a: '学', 0x1e80fbbd: '遠', 0x1f25c76c: '鉄',
    0x1f87934e: '強', 0x1f9fc6bf: '昨', 0x1fb18b4a: '汝', 0x2087125b: '脳',
    0x208ccb48: '移', 0x20f2729a: '亜', 0x210e8489: '島', 0x21253585: '素',
    0x216b22e0: '加', 0x216da260: '成', 0x21c4b4d6: '際', 0x2204687a: '祈',
    0x227c0829: '乏', 0x227c553f: '号', 0x22a017fa: '鋭', 0x22c47329: '刻',
    0x22db106a: '衰', 0x22db36b0: '亡', 0x22fb4b39: '模', 0x2315b336: '姉',
    0x232ae583: '酋', 0x23d6b5dd: '仮', 0x23f33497: '捜', 0x2401a54b: '欲',
    0x2415e9b5: '惜', 0x243b718d: '捕', 0x245b41d1: '考', 0x24e70688: '突',
    0x2520a949: '台', 0x2535ff97: '器', 0x254ae645: '殊', 0x2553e93e: '山',
    0x2555fb54: '盟', 0x25c7ecdf: '浅', 0x25dd4daa: '抑', 0x2603aa1c: '唱',
    0x26157bba: '僕', 0x2681fa57: '仕', 0x269ad173: '痴', 0x26e34115: '楽',
    0x26e858c7: '管', 0x27200cae: '航', 0x272b9f7e: '苦', 0x275ba155: '近',
    0x278a4217: '厚', 0x278e0eb9: '容', 0x2796c081: '字', 0x27b085a7: '猛',
    0x27b4d1f2: '天', 0x27cbd264: '震', 0x2816810a: '皮', 0x288cb8f9: '味',
    0x28cfa472: '測', 0x28eb9551: '位', 0x291c2c7b: '終', 0x292886a9: '冷',
    0x292a8a59: '械', 0x2946eb93: '吟', 0x299f65da: '週', 0x29a438f0: '拡',
    0x29e05be5: '赦', 0x29e729ff: '夫', 0x2a20efd3: '粗', 0x2a23405f: '舎',
    0x2a61b800: '碑', 0x2a6cf7d7: '護', 0x2a7d45e8: '説', 0x2aca9572: '下',
    0x2adf1bf8: '妹', 0x2b15fe3a: '大', 0x2b700819: '委', 0x2b7b98ae: '腹',
    0x2c14cc90: '捨', 0x2c377dd4: '冶', 0x2c7e5bf1: '得', 0x2cc9bcd7: '壊',
    0x2cd15301: '改', 0x2cea9f0b: '倉', 0x2d05dde9: '急', 0x2d245666: '帯',
    0x2daf7a8b: '運', 0x2dca695d: '杯', 0x2ddad0b2: '次', 0x2e33fa27: '似',
    0x2f24afc2: '分', 0x2f4467f0: '走', 0x2f53b03b: '造', 0x2f776dad: '失',
    0x2f9eea6c: '折', 0x2fcf5e85: '宝', 0x2fefdfba: '占', 0x30092e6d: '箱',
    0x30324e2b: '出', 0x3093698b: '触', 0x3098f717: '個', 0x30d74747: '叫',
    0x3113552e: '牧', 0x31289ad4: '商', 0x3193b0c6: '廃', 0x31ac08db: '預',
    0x32964a08: '室', 0x32ae92e5: '輝', 0x32b4f4ed: '努', 0x3318d664: '飼',
    0x33720cbe: '乗', 0x338233d8: '切', 0x33adf80c: '松', 0x34417b14: '絆',
    0x346a8b22: '弟', 0x34748f1d: '覇', 0x34a23ec4: '田', 0x34f58ae9: '砂',
    0x3508dbf0: '雨', 0x350ab097: '宮', 0x35230e3d: '極', 0x35a6d56c: '託',
    0x35a94795: '葉', 0x35fdd1a3: '純', 0x362af680: '輸', 0x36347c05: '若',
    0x3685d12a: '株', 0x36918749: '浪', 0x36c5e84a: '庫', 0x36dea405: '髪',
    0x372d7ab1: '偶', 0x372df1b6: '貌', 0x374da768: '殺', 0x375bc718: '莫',
    0x37a0a9b7: '沈', 0x380288bc: '産', 0x3882d953: '幡', 0x38ca320a: '利',
    0x38d419ce: '岩', 0x38e55a3d: '開', 0x3927ba0a: '船', 0x396b04a7: '枯',
    0x397f68d5: '慈', 0x399655c3: '父', 0x399ccbd1: '扉', 0x39ba0ac6: '団',
    0x39d75130: '院', 0x3a053caf: '勝', 0x3a595328: '済', 0x3a8fa223: '根',
    0x3aa923df: '奪', 0x3aaa59d9: '尽', 0x3ab7622a: '区', 0x3abb6a52: '鳥',
    0x3ad4b838: '訴', 0x3ae34f2f: '階', 0x3aee008b: '秒', 0x3af93a6c: '編',
    0x3b128ad2: '拓', 0x3b398013: '懲', 0x3b6b9d8f: '差', 0x3b7514c7: '在',
    0x3b9b8235: '勘', 0x3c0a450a: '取', 0x3c637695: '審', 0x3c85e696: '咲',
    0x3cd87aee: '災', 0x3d10234f: '久', 0x3d2564cd: '羽', 0x3d2c31ce: '鉱',
    0x3d54e05d: '便', 0x3d585dc8: '怪', 0x3d5c041c: '看', 0x3d84d41b: '償',
    0x3dc342d3: '井', 0x3e2b97ca: '湖', 0x3e40b8fe: '己', 0x3e62a047: '晴',
    0x3eedebd8: '全', 0x3f0ae4d5: '席', 0x3f2d118c: '五', 0x3f2f1f55: '仁',
    0x3f594110: '氏', 0x3f8a87e0: '無', 0x3fb3e400: '傷', 0x3fbda68d: '揃',
    0x3fda5d5e: '宣', 0x4023f975: '建', 0x406a69e0: '醒', 0x40a4c82a: '況',
    0x40c7178a: '聴', 0x40cf28ca: '群', 0x40f924b8: '辛', 0x416776c7: '塩',
    0x416e3c12: '竹', 0x4178e848: '有', 0x4196b4c1: '笑', 0x41a6bb28: '続',
    0x41c6d367: '候', 0x4238724d: '栗', 0x4245448d: '包', 0x428c4c76: '私',
    0x429942c9: '花', 0x42dcf065: '簡', 0x42de90e3: '必', 0x437e4e45: '渉',
    0x43a9d728: '貫', 0x43ce537d: '援', 0x442ff962: '誌', 0x444afad4: '菌',
    0x446bd791: '米', 0x44715f2e: '休', 0x4474280e: '換', 0x44882cad: '報',
    0x44909590: '至', 0x44941a39: '嫌', 0x44bc1e6a: '婦', 0x44d4392f: '抗',
    0x44dce76f: '話', 0x4547f95f: '宅', 0x45af05fe: '葬', 0x45c40c9e: '逃',
    0x45caf652: '庶', 0x45cf915b: '臣', 0x45eceef6: '消', 0x4611b986: '最',
    0x46231aeb: '信', 0x4664d29e: '散', 0x4676f8be: '四', 0x46bea61e: '専',
    0x46db032d: '盾', 0x46eb5d53: '沿', 0x4714e7eb: '春', 0x4781dcd0: '質',
    0x47aa70ad: '献', 0x47cc5044: '具', 0x47ce5fb1: '牢', 0x47d50e25: '執',
    0x4825eb71: '袋', 0x487e4713: '我', 0x48c48408: '殼', 0x48de90b7: '争',
    0x49565ac8: '途', 0x49911237: '撃', 0x49a28759: '紛', 0x49c87691: '倫',
    0x49e003ef: '伊', 0x4a1801c3: '世', 0x4a220a8a: '戴', 0x4a64d466: '認',
    0x4a8befdc: '讐', 0x4aa5330d: '宿', 0x4ab2ac10: '緒', 0x4aebe29d: '設',
    0x4b334111: '満', 0x4b669f95: '溶', 0x4b742fbc: '頭', 0x4bbbccdf: '紀',
    0x4bdec539: '各', 0x4c204e65: '涯', 0x4c2a1e02: '火', 0x4d2fce5b: '遺',
    0x4d44f76b: '峰', 0x4d87bf00: '効', 0x4dc497f3: '持', 0x4ddf03c2: '講',
    0x4e059267: '友', 0x4e187961: '作', 0x4e4a71b2: '吉', 0x4e56230a: '交',
    0x4e5fcaec: '象', 0x4eacab1b: '茶', 0x4eba2ed6: '険', 0x4edd8d42: '細',
    0x4f47f767: '譲', 0x4f4acf43: '着', 0x4f551dd1: '験', 0x4f5d1b12: '定',
    0x4f859c54: '歳', 0x4fec32be: '陽', 0x4ffb2005: '鍵', 0x501ebc0d: '意',
    0x502b49cb: '自', 0x5048abc5: '余', 0x50be4f32: '蓄', 0x510699f9: '繰',
    0x511baa13: '合', 0x513e1b9d: '砦', 0x514c0e60: '単', 0x518849fc: '聖',
    0x51b34609: '征', 0x51cf3d18: '前', 0x51e7ea54: '先', 0x52e1b297: '掃',
    0x53260d8b: '議', 0x53366a4d: '城', 0x53376231: '返', 0x534b45e4: '公',
    0x534e2341: '氷', 0x53554567: '句', 0x539d1138: '悦', 0x53ab46e3: '該',
    0x53d9269f: '旧', 0x53ff4ff5: '壇', 0x54314f5d: '王', 0x547b9bf8: '昔',
    0x549205e0: '座', 0x54dd7fc3: '燃', 0x550ff180: '障', 0x554eab57: '牲',
    0x5560ce8e: '副', 0x5566ce4b: '代', 0x55697b05: '除', 0x5588b73a: '製',
    0x558de3b3: '仰', 0x55999cf4: '以', 0x559b958d: '界', 0x55c474a9: '短',
    0x55fa1b3d: '央', 0x5602c0aa: '長', 0x563de018: '潜', 0x564a4663: '拳',
    0x5676bff4: '級', 0x568366f7: '扱', 0x569b27b4: '漠', 0x56a9a744: '晩',
    0x56b023fe: '積', 0x56fc500a: '渦', 0x572c3720: '索', 0x5788b66e: '採',
    0x57c6496d: '暖', 0x57c92f47: '防', 0x57d678e8: '残', 0x57e79752: '幼',
    0x57f4b607: '神', 0x581d6d7e: '喰', 0x583f4507: '嵐', 0x58538c01: '鬼',
    0x58ef04d1: '植', 0x58f2c329: '漫', 0x594a0c19: '継', 0x594e632d: '章',
    0x596b7938: '没', 0x599195e8: '兵', 0x59c7c4fd: '絡', 0x59c9a9b7: '種',
    0x59df934b: '男', 0x59e49d69: '込', 0x59e4c6c7: '順', 0x59fd8a57: '式',
    0x5a15e03d: '訳', 0x5a74db96: '変', 0x5b1aae46: '職', 0x5b52c28c: '奏',
    0x5ba28b2c: '涙', 0x5c585cd1: '完', 0x5c65ff8c: '員', 0x5c6fd7d0: '厳',
    0x5c7128ad: '送', 0x5cb83562: '阻', 0x5cd71f43: '離', 0x5cf03d8c: '医',
    0x5d022b36: '払', 0x5d1be06f: '病', 0x5d7aa217: '士', 0x5d7dbdaa: '甘',
    0x5d93e521: '辺', 0x5d9e2512: '誰', 0x5d9fc8c5: '度', 0x5de1c91d: '察',
    0x5de96cf1: '囲', 0x5e1d6c0d: '毒', 0x5e2de501: '陸', 0x5e2debc2: '革',
    0x5e61d49d: '廊', 0x5e6f2eed: '迫', 0x5e9b3492: '結', 0x5ecc2244: '責',
    0x5ed56a65: '門', 0x5ee793e7: '伝', 0x5f5c649e: '後', 0x5f93c05b: '直',
    0x5fbf86dc: '技', 0x5fdced23: '華', 0x5fe2a3a5: '如', 0x5fe64f0f: '耳',
    0x6003dffc: '癒', 0x6010f487: '爵', 0x606d99f2: '冗', 0x60716665: '錬',
    0x609b3d38: '基', 0x60c8c21f: '妖', 0x60c99194: '所', 0x60d19a94: '停',
    0x60d6fb4b: '陰', 0x60ee86b7: '筋', 0x61087856: '犠', 0x61236941: '使',
    0x618026c2: '渓', 0x61baa57e: '班', 0x61d14300: '癖', 0x6238df4e: '業',
    0x624b2a6b: '普', 0x624caec4: '伏', 0x628ab57a: '江', 0x62a5ea14: '紋',
    0x62b70d12: '欠', 0x632e5be9: '恨', 0x63f25923: '宴', 0x641a7d72: '然',
    0x648e46e7: '塊', 0x64cf6bd0: '染', 0x65187bf4: '追', 0x65305dcb: '復',
    0x655aabf1: '難', 0x659f7cc5: '症', 0x65a9c839: '踊', 0x65b2bba7: '疑',
    0x65f51761: '魂', 0x66031b38: '勤', 0x664fcf1e: '遭', 0x66538e3d: '斬',
    0x66700d71: '庵', 0x66a1c35f: '本', 0x66a76e8b: '簿', 0x66aeca08: '操',
    0x66c75713: '躍', 0x66cd72fe: '炉', 0x66d63a1c: '違', 0x66ed2d5e: '妄',
    0x672876ef: '衝', 0x672d3200: '舞', 0x678528be: '拒', 0x679b78ca: '朽',
    0x67a615d9: '鼻', 0x68154f6f: '像', 0x68195500: '穏', 0x6857edd1: '績',
    0x687dda33: '君', 0x6888fe40: '黙', 0x68d2cfaf: '並', 0x690b740c: '小',
    0x690c1d37: '虹', 0x69800e2c: '指', 0x69bab1c7: '車', 0x69c61764: '速',
    0x69d6c398: '血', 0x6a229a39: '裏', 0x6a69ac2b: '脈', 0x6a740f69: '六',
    0x6ad17af8: '稼', 0x6af06caf: '狼', 0x6af9cece: '初', 0x6b02e584: '奥',
    0x6b41a6c3: '徒', 0x6b44e830: '関', 0x6b56d358: '邪', 0x6b6a0f51: '等',
    0x6b70c650: '戯', 0x6bb35853: '仙', 0x6bc09d72: '補', 0x6bff9178: '到',
    0x6c3be4f2: '響', 0x6c80be77: '津', 0x6c8ac459: '婚', 0x6cd4c9e0: '未',
    0x6cded06a: '悩', 0x6cf9966a: '低', 0x6d7c118d: '石', 0x6d9abe83: '土',
    0x6e28ad49: '紅', 0x6e2f889c: '叉', 0x6ed7368a: '気', 0x6ee71d6e: '基',
    0x6eecee36: '就', 0x6ef4b7d3: '能', 0x6ff34654: '八', 0x7002e4b2: '脅',
    0x7021a344: '爪', 0x705ca43f: '畑', 0x70974a75: '圏', 0x709f1709: '警',
    0x70b8aa30: '序', 0x70ebc2c1: '蘇', 0x710d6b00: '隠', 0x713576b4: '窪',
    0x71af2041: '千', 0x71b85b00: '発', 0x71bff0aa: '腰', 0x71dc6cd3: '閉',
    0x72005c7f: '映', 0x72145fe7: '窟', 0x72693550: '替', 0x7275cfa0: '給',
    0x72b7dbd7: '黒', 0x72c78ca2: '与', 0x739df19e: '豪', 0x73cb0007: '姫',
    0x73d0b8f3: '塚', 0x73dad3f7: '為', 0x749fb842: '客', 0x74a8d809: '緩',
    0x74c305d2: '攻', 0x74ce5c2d: '療', 0x754d7936: '侵', 0x75b7d548: '底',
    0x76079bd0: '充', 0x762e1a50: '鋼', 0x7649c0c4: '尊', 0x765bf3e5: '刺',
    0x76a573b2: '臓', 0x76bdf59c: '率', 0x76dbb9b9: '泉', 0x7704ab1d: '卿',
    0x770c0aa4: '他', 0x7716f468: '件', 0x776f754f: '凍', 0x779f6324: '良',
    0x77b87db2: '推', 0x7856c720: '蛇', 0x785938d7: '床', 0x786f07ec: '張',
    0x78a6152f: '連', 0x78a8637b: '人', 0x78ae3d8e: '鳴', 0x79816469: '去',
    0x79df9a37: '逮', 0x79e75afa: '摂', 0x7a012db1: '堀', 0x7a0cdfc1: '衛',
    0x7a2bf0bb: '揺', 0x7a3fc39f: '日', 0x7a5b38fc: '眠', 0x7a5d32fd: '割',
    0x7acaf5b5: '篭', 0x7ae27a9f: '担', 0x7ae6d619: '慄', 0x7b8645e6: '女',
    0x7b9c82c9: '参', 0x7bbf7816: '遥', 0x7be9f349: '波', 0x7c5e8650: '樹',
    0x7c83a84e: '呪', 0x7ca46b99: '海', 0x7cc8289d: '含', 0x7cd00aa7: '間',
    0x7cdfff20: '曲', 0x7d1b3ad7: '救', 0x7d67235d: '益', 0x7d8ecf9c: '希',
    0x7d94a682: '棺', 0x7d9d7468: '馬', 0x7dc2e79f: '元', 0x7de74160: '品',
    0x7e0614cb: '養', 0x7e28db0b: '描', 0x7e2b6042: '表', 0x7e2ba1ad: '漁',
    0x7e681a85: '惨', 0x7e73467b: '俊', 0x7e9d3fc2: '様', 0x7ed7b535: '賞',
    0x7f083f92: '搭', 0x7f14e6a4: '星', 0x7f2c3fb3: '荷', 0x7f8a60ce: '備',
    0x7f9c8624: '万', 0x7fbe2bfb: '肉', 0x801df9dc: '冒', 0x804874f1: '律',
    0x807afb54: '派', 0x80e55938: '紫', 0x8116f31c: '適', 0x818785c6: '承',
    0x81dbbc4c: '脚', 0x8207574e: '潮', 0x82477abc: '決', 0x827e7e7f: '背',
    0x8297c82f: '挑', 0x8319da42: '灯', 0x837e8f21: '平', 0x83b7c278: '礼',
    0x83f1ba66: '懸', 0x84112685: '巡', 0x841b08e2: '更', 0x84215d17: '鈴',
    0x848bd887: '傾', 0x849ad71a: '齢', 0x849f5d6b: '圧', 0x84b6ebde: '怨',
    0x84dafdc8: '忙', 0x84db00b9: '箇', 0x84e4daa6: '高', 0x85400e72: '糸',
    0x85df7dab: '栄', 0x85ee2f92: '酬', 0x8615b07c: '木', 0x861cc27a: '博',
    0x863241f8: '損', 0x8668007f: '板', 0x866e995b: '逐', 0x86eff93a: '即',
    0x8761e34c: '匠', 0x87694454: '興', 0x87848b80: '退', 0x87f4e1a4: '戦',
    0x87f91d31: '立', 0x8818c4cd: '浜', 0x881bb053: '申', 0x882cf83a: '示',
    0x883f4efa: '功', 0x886c4954: '東', 0x88854560: '劫', 0x88a22059: '母',
    0x88b3423d: '常', 0x88dae28f: '悔', 0x893e07b2: '和', 0x89a0c10a: '北',
    0x8a00d3ee: '動', 0x8a185c4a: '肝', 0x8a704fe9: '嫉', 0x8a73b494: '呼',
    0x8a95c959: '寝', 0x8aad599f: '社', 0x8ad1a500: '協', 0x8b027c69: '貸',
    0x8b293062: '寂', 0x8b758aae: '引', 0x8bad3dec: '育', 0x8bcae185: '修',
    0x8bec300a: '徴', 0x8bf9f393: '巨', 0x8c05044d: '撒', 0x8c1df2c9: '役',
    0x8c3ed2cf: '幹', 0x8c5f8ec7: '孝', 0x8c9813a2: '篤', 0x8ca0c50a: '活',
    0x8d44843e: '諸', 0x8d5d6621: '判', 0x8da376b5: '称', 0x8df22ac3: '施',
    0x8e1a7ade: '瞬', 0x8e36aab5: '粒', 0x8e4364cc: '暗', 0x8e46cf06: '証',
    0x8e6af47b: '誇', 0x8eed74a7: '量', 0x8f26bff7: '営', 0x8f6a4b29: '応',
    0x8f9a75c7: '般', 0x900b319c: '身', 0x90122902: '印', 0x9027842e: '術',
    0x9031a7b8: '裕', 0x903ebf58: '音', 0x90512948: '獣', 0x9080022b: '英',
    0x90827f65: '架', 0x909785db: '売', 0x909a7ee3: '杉', 0x90a44d91: '唄',
    0x90c64f69: '酒', 0x91032405: '別', 0x914a9d5f: '還', 0x91675764: '藤',
    0x917f18a2: '辱', 0x91d37b8c: '宇', 0x91f70191: '狭', 0x922b4891: '風',
    0x9235e51b: '戒', 0x92753ca6: '卑', 0x92acf13d: '杖', 0x92d69b42: '登',
    0x92ef2698: '軽', 0x9323fd34: '繁', 0x934467c6: '互', 0x9384f1be: '漂',
    0x939e135a: '拝', 0x93a7aa60: '招', 0x93dad5b5: '淡', 0x9406026f: '頓',
    0x940833ef: '儀', 0x94b47e71: '厨', 0x94b6e13e: '族', 0x94d3f62b: '犬',
    0x94d5a7fa: '忘', 0x94e7c71e: '部', 0x950b468f: '教', 0x95484ef1: '吐',
    0x95c99644: '提', 0x95cb9cab: '受', 0x964055b1: '焦', 0x9653207e: '段',
    0x9655e196: '裂', 0x9672ebab: '愛', 0x96bea4ef: '駆', 0x96ea5d60: '費',
    0x9727284b: '掌', 0x977fbd41: '言', 0x97b3ad05: '敬', 0x97d539b7: '左',
    0x97d641ec: '盗', 0x97decb03: '案', 0x980b501c: '堕', 0x981f0c3e: '徹',
    0x98b6487a: '願', 0x98b980ee: '緑', 0x98e4a4ec: '進', 0x9940421f: '奴',
    0x9941ee83: '賑', 0x99944d94: '予', 0x999e61ed: '束', 0x99b3891a: '計',
    0x99dfba0c: '吹', 0x9a0d7cec: '炎', 0x9a2b1585: '居', 0x9a34012d: '妻',
    0x9a4ad779: '閃', 0x9ac4c82a: '刑', 0x9adba9af: '月', 0x9b3bb5b2: '覧',
    0x9b3cc8d0: '優', 0x9b566f96: '糧', 0x9b763fc7: '題', 0x9b8ef002: '影',
    0x9bb1d467: '陥', 0x9bb65fc3: '康', 0x9bdf159b: '忠', 0x9bf90db3: '名',
    0x9c493609: '豆', 0x9c910c1f: '道', 0x9d184ef1: '資', 0x9d6aa281: '確',
    0x9d965c1a: '外', 0x9e09f33f: '祝', 0x9e0a567a: '討', 0x9e37d02e: '肩',
    0x9e55b5a6: '骨', 0x9e617fb5: '書', 0x9e657375: '隔', 0x9ebd177b: '及',
    0x9eca8e89: '的', 0x9ecd4ade: '粉', 0x9f69c1d5: '保', 0x9f6dc7cb: '免',
    0x9f8c464d: '導', 0x9ff1defc: '反', 0xa0393d04: '性', 0xa03a4b24: '用',
    0xa057ef9d: '締', 0xa080b132: '百', 0xa0a5494d: '番', 0xa12beb6d: '浄',
    0xa1472660: '雌', 0xa15ce83a: '町', 0xa182a578: '紙', 0xa25d9adb: '灼',
    0xa322e5af: '工', 0xa34913ca: '形', 0xa3b996a2: '村', 0xa3f29830: '恥',
    0xa4cc49da: '貧', 0xa4db3e18: '誓', 0xa580cfdc: '詮', 0xa58498df: '酷',
    0xa5ddabdc: '悲', 0xa68995b3: '溜', 0xa6caf850: '宙', 0xa6dd850f: '超',
    0xa6ea3945: '劣', 0xa7025944: '力', 0xa7084840: '軟', 0xa70b37f4: '雪',
    0xa724b72c: '線', 0xa73589b4: '腕', 0xa79a60cd: '干', 0xa81706da: '輪',
    0xa8aad0d9: '谷', 0xa8d6af8a: '恋', 0xa900496c: '存', 0xa91653c2: '型',
    0xa9275ad3: '巻', 0xa94db376: '励', 0xa961b909: '手', 0xa9d3a61e: '詳',
    0xa9fdd163: '通', 0xaa297abf: '聞', 0xaa78cfc2: '疫', 0xaa8d5246: '覆',
    0xaa9aba87: '陣', 0xaaa6eec3: '心', 0xaaaa7f95: '夷', 0xaab91dc8: '怖',
    0xaaba1b11: '尾', 0xabc9fce5: '渋', 0xabf51dd1: '抵', 0xabf7c3df: '声',
    0xac2398dc: '混', 0xac31e1dc: '国', 0xac4f10dc: '遅', 0xac5d8541: '棄',
    0xac6bd2fb: '球', 0xac7a9355: '歌', 0xacb06d58: '巫', 0xacd197fa: '非',
    0xad358f9a: '悠', 0xad44d16f: '志', 0xad63f7ed: '誉', 0xad704347: '眼',
    0xadc6224d: '掛', 0xade31123: '郎', 0xae10163a: '鎮', 0xae2035f5: '原',
    0xae3cc810: '善', 0xae91c38f: '絶', 0xaea082db: '趣', 0xaea58bba: '敵',
    0xaef933ef: '掲', 0xaefe9539: '虎', 0xaf0c0561: '易', 0xaf391da7: '比',
    0xaf40e336: '択', 0xaf49b33b: '経', 0xaf503715: '達', 0xaf8f0a53: '司',
    0xafa84df7: '属', 0xafc77d8e: '複', 0xb001f1c8: '列', 0xb025e410: '評',
    0xb03c89cf: '首', 0xb05c7655: '朝', 0xb05fafdb: '対', 0xb0dfce0d: '催',
    0xb1762a55: '格', 0xb1ca443c: '郷', 0xb2319f7c: '過', 0xb2338e14: '校',
    0xb237ce1f: '汚', 0xb2889c83: '地', 0xb297d0f9: '正', 0xb2b59f0e: '境',
    0xb2d1182f: '縄', 0xb2ddf8e5: '述', 0xb2f2841a: '里', 0xb2f64dc5: '獲',
    0xb2f8f8b2: '物', 0xb323b917: '慢', 0xb334aa2c: '行', 0xb34fb0fa: '携',
    0xb3a3f6b3: '巣', 0xb3b14d3b: '魔', 0xb3e0dc73: '授', 0xb43dfe28: '枠',
    0xb4ac13f0: '上', 0xb4b80245: '哲', 0xb560c04c: '師', 0xb57e9407: '頂',
    0xb5b85b6f: '円', 0xb5d641a5: '致', 0xb5ded380: '仇', 0xb62ef02b: '牙',
    0xb646ba10: '帳', 0xb70c2bda: '材', 0xb70d517c: '昇', 0xb7717af5: '息',
    0xb792c712: '義', 0xb7b6f4c3: '倍', 0xb7c93216: '民', 0xb7d3089e: '勲',
    0xb7dda09e: '昼', 0xb7f87984: '墜', 0xb87e8bbc: '安', 0xb8a850ef: '再',
    0xb9056322: '一', 0xb90c251f: '也', 0xb993f1b8: '南', 0xb9a15e40: '料',
    0xb9b5035e: '晶', 0xb9bbfb40: '水', 0xb9c7dafb: '雰', 0xb9ea56d9: '角',
    0xba1536a7: '年', 0xba241fa0: '殖', 0xba298bb1: '軍', 0xba3234ae: '督',
    0xba5406fd: '耐', 0xba624ecb: '獄', 0xbb31bc79: '層', 0xbb4eb845: '例',
    0xbb6e78af: '源', 0xbb91a838: '伸', 0xbb9c7f52: '共', 0xbb9ca2c8: '増',
    0xbbcf9ebc: '識', 0xbbe73874: '果', 0xbc319840: '片', 0xbcfb8f40: '額',
    0xbd2c986b: '焼', 0xbd4aa3a8: '翔', 0xbd54ccfa: '夜', 0xbe290ede: '納',
    0xbe5b27ed: '謎', 0xbe6e184e: '錯', 0xbe7a57e0: '監', 0xbeafe572: '曇',
    0xbedd481c: '歯', 0xbf487c06: '係', 0xbfba90bf: '詩', 0xc0115be3: '真',
    0xc040e8a2: '川', 0xc05b1594: '激', 0xc0720d7c: '旋', 0xc08e3fbb: '捧',
    0xc0a89425: '程', 0xc0fc5464: '状', 0xc10a4ae2: '節', 0xc12278d8: '抜',
    0xc207350c: '瀬', 0xc20aa75d: '糸', 0xc21f55c1: '偏', 0xc233ed5c: '旅',
    0xc2781251: '画', 0xc2c71ce3: '延', 0xc2fb7862: '制', 0xc3744385: '読',
    0xc3748d04: '刃', 0xc405f098: '側', 0xc44870f5: '尻', 0xc46c1342: '唯',
    0xc4a4455d: '敗', 0xc4bc833e: '傑', 0xc5448dc7: '由', 0xc59ad332: '買',
    0xc5ffaf24: '粋', 0xc62ca35c: '老', 0xc6c78491: '知', 0xc6d64e18: '録',
    0xc6ef74ee: '患', 0xc6f5b2df: '金', 0xc6f8b679: '草', 0xc7101547: '選',
    0xc74bc7cd: '幸', 0xc75914c0: '任', 0xc7809eb5: '揮', 0xc7d7bc88: '彦',
    0xc7fd14b9: '止', 0xc8134c24: '局', 0xc8165e58: '路', 0xc852685f: '健',
    0xc8b42418: '挙', 0xc8e6d134: '歴', 0xc94088e5: '創', 0xca37cfac: '調',
    0xca90aa14: '洞', 0xcac368a6: '玉', 0xcb49a1c2: '食', 0xcb5c9440: '胸',
    0xcb6972db: '膨', 0xcb8127f9: '市', 0xcbd9fb48: '偽', 0xcbe35f00: '疾',
    0xcc6a3002: '森', 0xcc7f6744: '幻', 0xcc8b4f7e: '賃', 0xcc9b64ed: '飲',
    0xcca05bb5: '薬', 0xccb13f61: '望', 0xccc2855e: '逆', 0xccdccec2: '控',
    0xcd16afe2: '情', 0xcd197778: '助', 0xcd3a138c: '観', 0xcd7806a7: '贈',
    0xcdb8421f: '剣', 0xcdc82d53: '菊', 0xcdd8cd35: '官', 0xcdf5c2c7: '兼',
    0xce013709: '投', 0xce2741f3: '右', 0xce3f0b41: '鈍', 0xce5577ed: '烈',
    0xce9a3e80: '快', 0xcf175d9d: '酔', 0xcf20a85a: '明', 0xcf7769fd: '生',
    0xcf83fb70: '実', 0xd0079142: '避', 0xd01fa05e: '喜', 0xd024944d: '領',
    0xd04b447a: '会', 0xd0eb1cbe: '足', 0xd0eeeb1d: '枚', 0xd110b6e8: '照',
    0xd1385e2a: '雷', 0xd14ea632: '襲', 0xd1908202: '憶', 0xd1dac94c: '園',
    0xd1dd4785: '処', 0xd1ddfc91: '札', 0xd1fa0b93: '叙', 0xd22292d0: '惑',
    0xd236c277: '狩', 0xd271ffc9: '浮', 0xd2dce1e0: '跡', 0xd2fcfe7e: '総',
    0xd324983e: '第', 0xd36a3c99: '遂', 0xd383436b: '瞳', 0xd390fe73: '俺',
    0xd3de864e: '殿', 0xd3df7029: '従', 0xd45d0f1d: '距', 0xd467c029: '悟',
    0xd4adf928: '支', 0xd4c385b0: '親', 0xd4c9270f: '奇', 0xd4dd9214: '豊',
    0xd5062f1b: '借', 0xd51bd7f1: '主', 0xd526325a: '面', 0xd5448d7c: '異',
    0xd5528a34: '渡', 0xd59436e1: '写', 0xd5a76a33: '版', 0xd5e6fb16: '要',
    0xd610c1dc: '誕', 0xd63baec5: '慕', 0xd67b9947: '赤', 0xd69e0cfb: '密',
    0xd763c610: '留', 0xd7b21846: '談', 0xd7bc6ac7: '勢', 0xd7e2fc62: '脱',
    0xd7f961b1: '媒', 0xd7ffc4d0: '被', 0xd814c60e: '砲', 0xd8298a4e: '珍',
    0xd83d99c4: '不', 0xd844eb5d: '胞', 0xd8692cd1: '青', 0xd88fb9c0: '叩',
    0xd8ec66dc: '罪', 0xd91b2c53: '妨', 0xd956bdda: '想', 0xd9abc4df: '絵',
    0xd9e34ab9: '槍', 0xda4d30ec: '塔', 0xda639979: '訪', 0xda9b3625: '接',
    0xdb26df7f: '文', 0xdb2c9450: '謝', 0xdb5947f1: '孤', 0xdb80fd98: '向',
    0xdbab7c1a: '覚', 0xdbed7436: '拾', 0xdbf2e17d: '詞', 0xdc46e35c: '秀',
    0xdceb6a72: '雲', 0xdcef4e28: '視', 0xdd70cdb8: '翌', 0xdd808361: '卒',
    0xde1ed738: '虚', 0xde5b25c7: '愚', 0xde79b771: '闇', 0xde8ce6ca: '介',
    0xdec15e9f: '武', 0xdeef44ea: '場', 0xdf82e67e: '見', 0xdfbeb5f4: '末',
    0xdfec7614: '熱', 0xdff47b8a: '児', 0xe0016675: '岸', 0xe00d8245: '古',
    0xe06c34a5: '当', 0xe06c66c0: '光', 0xe07ad703: '務', 0xe08202a0: '思',
    0xe0839df9: '入', 0xe0b626f7: '多', 0xe1059c6c: '態', 0xe140cd08: '放',
    0xe17ae48c: '精', 0xe1801129: '断', 0xe1fbc123: '始', 0xe24fed73: '忌',
    0xe29ec902: '美', 0xe2e06fb6: '織', 0xe2e4436a: '置', 0xe30f1098: '陛',
    0xe32679ba: '端', 0xe355a2d5: '押', 0xe399f0e3: '駄', 0xe3d2fda0: '芸',
    0xe3ea458c: '早', 0xe422e767: '翼', 0xe432e6de: '時', 0xe4540430: '摘',
    0xe456ff00: '賊', 0xe516fbe9: '魚', 0xe538447c: '骸', 0xe56c5706: '載',
    0xe59bbf63: '壁', 0xe5e2915a: '深', 0xe5f06a66: '飛', 0xe6066355: '棒',
    0xe6329c3c: '回', 0xe6476ac2: '告', 0xe649127b: '色', 0xe656371a: '沖',
    0xe6a27c92: '弾', 0xe6a6a622: '打', 0xe6b3b7f5: '現', 0xe6d3352e: '値',
    0xe6fec4b1: '飾', 0xe70b7193: '鳩', 0xe7165eca: '働', 0xe731d424: '来',
    0xe740236a: '握', 0xe7474a3b: '静', 0xe79f6c2f: '感', 0xe819ba0a: '乱',
    0xe81c3627: '秘', 0xe83558fb: '彰', 0xe8410d77: '類', 0xe8529a6f: '縦',
    0xe86378cb: '治', 0xe86b8771: '周', 0xe8a42809: '倒', 0xe8b06efb: '獅',
    0xe8c5aaef: '淵', 0xe8d8278d: '街', 0xe8dc1bc2: '忍', 0xe8e057f5: '服',
    0xe9102709: '項', 0xe9839103: '犯', 0xe987cd30: '屋', 0xea074080: '賢',
    0xea399cb3: '許', 0xea74a7c5: '困', 0xeab96d2a: '空', 0xeacd6654: '付',
    0xeb046dcc: '詠', 0xeb6f6d46: '誘', 0xeb70f246: '滋', 0xebcc1e6a: '銭',
    0xec0ecee4: '減', 0xec3e7a85: '好', 0xec4f13dd: '解', 0xec625fd9: '暮',
    0xec829e76: '策', 0xec95f42c: '遇', 0xedc1013c: '答', 0xedc335eb: '孫',
    0xee025c46: '流', 0xee1a450a: '事', 0xee1e2342: '域', 0xee1f2d61: '三',
    0xee343277: '化', 0xee7dc55f: '壺', 0xee8d99d7: '子', 0xeec7ad68: '装',
    0xef63c309: '縁', 0xef74d676: '弘', 0xef791121: '広', 0xefb17db5: '横',
    0xeff7fc37: '堂', 0xf0526ea4: '布', 0xf05fddac: '勇', 0xf075c4cd: '祭',
    0xf0cfb4ba: '港', 0xf0eb3ec1: '因', 0xf1165983: '却', 0xf12ed97b: '電',
    0xf14ace6c: '伴', 0xf1580148: '契', 0xf16a5759: '穴', 0xf197043b: '維',
    0xf1a64c7c: '今', 0xf22a5b8d: '毛', 0xf23efee0: '価', 0xf24067c5: '権',
    0xf26564bb: '塞', 0xf26cdfd0: '者', 0xf2913265: '怒', 0xf29c4531: '竜',
    0xf2a5d6e6: '少', 0xf2ba8a88: '柔', 0xf2c8d58f: '念', 0xf32080f2: '菜',
    0xf39c6701: '崇', 0xf3c2667c: '皆', 0xf409674e: '愉', 0xf421da99: '相',
    0xf464e777: '寛', 0xf496504b: '頃', 0xf4d7d543: '供', 0xf4e87895: '何',
    0xf4f1bdea: '募', 0xf4f9b232: '祖', 0xf51a988a: '築', 0xf51d346b: '兄',
    0xf5287995: '約', 0xf52ae1a0: '可', 0xf5357e9a: '矢', 0xf53a83fd: '幅',
    0xf54d9d71: '盤', 0xf586172a: '虫', 0xf5976a90: '研', 0xf5b7c4dc: '恩',
    0xf5ba7986: '敷', 0xf6173fa4: '嫁', 0xf6285672: '否', 0xf660ff3e: '闘',
    0xf69e4363: '論', 0xf69eaee6: '振', 0xf6a39c1b: '省', 0xf6b58a6a: '禁',
    0xf701609e: '政', 0xf70e68f6: '寒', 0xf7116934: '標', 0xf7347ad5: '財',
    0xf78004ec: '縛', 0xf7c8c646: '恵', 0xf7e400a9: '雑', 0xf81ca800: '嘆',
    0xf85519e9: '疲', 0xf866b22b: '展', 0xf8904976: '鍛', 0xf9200405: '負',
    0xf9a8bc46: '笛', 0xf9f51489: '探', 0xf9fc845a: '害', 0xfa128ff5: '起',
    0xfa1dc499: '柱', 0xfa889186: '目', 0xfa9e58cb: '内', 0xfaa16130: '峡',
    0xfaae7f3c: '依', 0xfab5699e: '罰', 0xfabad410: '踏', 0xfaea19a0: '才',
    0xfaf259fa: '恐', 0xfb0521f5: '待', 0xfb76e252: '跳', 0xfb984160: '悪',
    0xfbc75443: '口', 0xfbc8313c: '環', 0xfc0b166e: '査', 0xfc101580: '肖',
    0xfc13685c: '丈', 0xfc20ba11: '庭', 0xfc4a036f: '橋', 0xfc69c6ba: '威',
    0xfc8066df: '薄', 0xfc948b8a: '仲', 0xfc9757a5: '戸', 0xfcb14e34: '暴',
    0xfcd610fc: '屈', 0xfd343808: '検', 0xfd48c0b2: '貴', 0xfd5a2c11: '家',
    0xfd7a6767: '酸', 0xfdc1749a: '越', 0xfde73278: '砕', 0xfde7a419: '痛',
    0xfe3f9189: '守', 0xfe619e63: '毎', 0xfeed4f99: '頼', 0xff6a0f30: '秩',
    0xff7e8a44: '叱', 0xffb8ebec: '落', 0xffe98fb1: '双',
}


# Decode text from the Japanese game version.
def decodeJP(data, kanjiBitmap):
    text = ""

    largeFont = False

    dataSize = len(data)

    i = 0
    while i < dataSize:
        c = data[i]
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
            sjis = bytes([0x82, c + 0x77])
            text += sjis.decode("sjis")

        elif c >= 0x81 and c <= 0x84:

            # SJIS double-byte code
            sjis = bytes([c, data[i]])
            i += 1
            text += sjis.decode("sjis")

        elif (c >= 0x88 and c <= 0x9f):

            # Kanji
            c2 = data[i]
            i += 1

            found = False

            if largeFont:

                # The large (PSX ROM) font uses standard SJIS encoding
                sjis = bytes([c, c2])
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
                    hash = zlib.crc32(kanjiBitmap[offset:offset + 22]) & 0xffffffff

                    try:
                        text += kanjiByHash[hash]
                        found = True
                    except KeyError:
                        print("Unknown Kanji %02x %02x" % (c, c2))
                        print("Hash = 0x%08x" % hash)
                        for y in range(11):
                            v = (kanjiBitmap[offset + y*2] << 8) | kanjiBitmap[offset + y*2 + 1]
                            s = ""
                            for x in range(16):
                                if v & 0x8000:
                                    s += "#"
                                else:
                                    s += "."
                                v <<= 1
                            print(s)
                        print()

            if not found:
                text += '{KANJI %02x %02x}' % (c, c2)

        elif c >= 0xa7 and c <= 0xdd:

            # Katakana
            text += katakana[c - 0xa7]

        else:

            # Unknown
            text += '{' + hex(c) + '}'

    return text


# International character set (variation of DOS code page 437)
#
# Note: The characters ÁÍÚ are from code page 850 and are used in the
# Spanish release although they are not actually present in the game's
# font.
origCharset = (
    " !\"#$%&'()*+,-./"  # 20..2f
    "0123456789:★<=>?"   # 30..3f
    "「ABCDEFGHIJKLMNO"  # 40..4f
    "PQRSTUVWXYZ[♂]』_"  # 50..5f
    "`abcdefghijklmno"   # 60..6f
    "pqrstuvwxyz{♀}『 "  # 70..7f
    "ÇüéâäàåçêëèïîìÄÅ"   # 80..8f
    "ÉæÆôöòûùÿÖÜ¢£¥▯ƒ"   # 90..9f
    "áíóúñÑªº¿▯¬½¼¡«»"   # a0..af
    "▯▯▯▯▯Á▯▯▯▯▯▯▯▯▯▯"   # b0..bf
    "▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯"   # c0..cf
    "▯▯▯▯▯▯Í▯▯▯▯▯▯▯▯▯"   # d0..df
    "▯ß▯¶▯▯µ▯▯Ú▯▯▯▯▯▯"   # e0..ef
    "▯±▯▯▯▯÷▯°∙▯▯▯▯▯▯"   # f0..ff
)

# Alternative character set (variation of DOS code page 850), designed for
# use with a custom font
altCharset = (
    " !\"#$%&'()*+,-./"  # 20..2f
    "0123456789:★<=>?"   # 30..3f
    "“ABCDEFGHIJKLMNO"   # 40..4f
    "PQRSTUVWXYZ[♂]’_"   # 50..5f
    "”abcdefghijklmno"   # 60..6f
    "pqrstuvwxyz{♀}‘ "   # 70..7f
    "ÇüéâäàåçêëèïîìÄÅ"   # 80..8f
    "ÉæÆôöòûùÿÖÜø£Ø▯ƒ"   # 90..9f
    "áíóúñÑªº¿▯~½¼¡«»"   # a0..af
    "▯▯▯▯▯ÁÂÀ▯▯▯▯▯▯▯▯"   # b0..bf
    "▯▯▯▯▯▯ãÃ▯▯▯▯▯▯▯▯"   # c0..cf
    "ðÐÊËÈ▯ÍÎÏ▯▯▯▯▯Ì▯"   # d0..df
    "ÓßÔÒõÕµþÞÚÛÙýÝœŒ"   # e0..ef
    "▯±…▯▯▯÷▯°∙▯▯▯▯▯▯"   # f0..ff
)

charset = origCharset

def setAltCharset():
    global charset
    charset = altCharset

# Characters which must be escaped when decoding
escapeChars = "\\{}"


# Decode text from the US or European game version.
def decodeINT(data):
    text = ""

    dataSize = len(data)

    i = 0
    while i < dataSize:
        c = data[i]
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
                text += "\\"

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
        raise EnvironmentError("Japanese text encoding is not supported")

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
                data.append(charset.index(c) + 0x20)
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

            # Find the command code
            try:
                code = codeOfCommand[keyword]
            except KeyError:
                raise ValueError("Unknown command '%s' in string '%s'" % (keyword, text))

            data.append(code)


            # Get the argument
            arg = None
            argLen = controlCodes[code][0]

            if argLen:
                m = re.match(keyword + r" (\d+)", command)
                arg = int(m.group(1))
            else:
                m = re.match(keyword, command)

            if not m:
                raise ValueError("Syntax error in command '%s' in string '%s'" % (command, text))

            if argLen:
                if arg < 0 or arg >= 10**argLen:
                    raise "Argument of %s command out of range in string '%s'" % (keyword, text)

                data.extend((b"%%0%dd" % argLen) % arg)

        else:

            # Regular printable character
            try:
                t = charset.index(c) + 0x20
                data.append(t)

                if (version == Version.US) and (t >= 0x80):
                    raise ValueError

            except ValueError:
                raise ValueError("Unencodable character '%s' in string '%s'" % (c, text))

    # Terminate string
    data.append(0)
    return data
