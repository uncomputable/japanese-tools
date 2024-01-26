import unittest
from typing import List

KATAKANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
"""
Katakana unicode block plus repetition marks
"""
HIRAGANA = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
"""
Hiragana unicode block plus repetition marks
"""
SHINJITAI = "亜悪圧囲為医壱逸稲飲隠営栄衛駅謁円縁艶塩奥応横欧殴黄温穏仮価禍画会壊悔懐海絵慨概拡殻覚学岳楽喝渇褐勧巻寛歓漢缶観関陥顔器既帰気祈亀偽戯犠旧拠挙虚峡挟狭郷響暁勤謹区駆勲薫径恵掲渓経継茎蛍軽鶏芸撃欠倹剣圏検権献研県険顕験厳効広恒鉱号国穀黒済砕斎剤桜冊殺雑参惨桟蚕賛残祉糸視歯児辞湿実舎写煮社者釈寿収臭従渋獣縦祝粛処暑緒署諸叙奨将渉焼祥称証乗剰壌嬢条浄状畳譲醸嘱触寝慎真神尽図粋酔随髄数枢瀬声静斉摂窃節専戦浅潜繊践銭禅曽祖僧双壮層捜挿巣争痩総荘装騒増憎臓蔵贈即属続堕体対帯滞台滝択沢単嘆担胆団弾断痴遅昼虫鋳著庁徴懲聴勅鎮塚逓鉄転点伝都党盗灯当闘徳独読突届縄難弐悩脳覇廃拝梅売麦発髪抜繁晩蛮卑碑秘浜賓頻敏瓶侮福払仏併塀並変辺勉弁弁弁舗歩穂宝褒豊墨没翻毎万満免麺黙餅戻弥薬訳予余与誉揺様謡来頼乱欄覧隆竜虜両猟緑塁涙類励礼隷霊齢暦歴恋練錬炉労廊朗楼郎録湾尭槙琢禄聡巌渚瑶禎遥晋猪祐穣"
KYUJITAI  = "亞惡壓圍爲醫壹逸稻飮隱營榮衞驛謁圓緣艷鹽奧應橫歐毆黃溫穩假價禍畫會壞悔懷海繪慨槪擴殼覺學嶽樂喝渴褐勸卷寬歡漢罐觀關陷顏器既歸氣祈龜僞戲犧舊據擧虛峽挾狹鄕響曉勤謹區驅勳薰徑惠揭溪經繼莖螢輕鷄藝擊缺儉劍圈檢權獻硏縣險顯驗嚴效廣恆鑛號國穀黑濟碎齋劑櫻册殺雜參慘棧蠶贊殘祉絲視齒兒辭濕實舍寫煮社者釋壽收臭從澁獸縱祝肅處暑緖署諸敍奬將涉燒祥稱證乘剩壤孃條淨狀疊讓釀囑觸寢愼眞神盡圖粹醉隨髓數樞瀨聲靜齊攝竊節專戰淺潛纖踐錢禪曾祖僧雙壯層搜插巢爭瘦總莊裝騷增憎臟藏贈卽屬續墮體對帶滯臺瀧擇澤單嘆擔膽團彈斷癡遲晝蟲鑄著廳徵懲聽敕鎭塚遞鐵轉點傳都黨盜燈當鬭德獨讀突屆繩難貳惱腦霸廢拜梅賣麥發髮拔繁晚蠻卑碑祕濱賓頻敏甁侮福拂佛倂塀竝變邊勉辨瓣辯舖步穗寶襃豐墨沒飜每萬滿免麵默餠戾彌藥譯豫餘與譽搖樣謠來賴亂欄覽隆龍虜兩獵綠壘淚類勵禮隸靈齡曆歷戀練鍊爐勞廊朗樓郞錄灣堯槇琢祿聰巖渚瑤禎遙晉猪祐穰"

KATA_TO_HIRA = str.maketrans(KATAKANA, HIRAGANA)
HIRA_TO_KATA = str.maketrans(HIRAGANA, KATAKANA)
SHIN_TO_KYU  = str.maketrans(SHINJITAI, KYUJITAI)
KYU_TO_SHIN  = str.maketrans(KYUJITAI, SHINJITAI)

def kata_to_hira(string: str) -> str:
    # XXX: Mapping from atomic to composite unicode symbols
    # Edit with care
    return string.replace("ヿ", "こと") \
        .replace("ヷ", "わ゙") \
        .replace("ヸ", "ゐ゙") \
        .replace("ヹ", "ゑ゙") \
        .replace("ヺ", "を゙") \
        .translate(KATA_TO_HIRA)

def hira_to_kata(string: str) -> str:
    # XXX: Mapping from composite to atomic unicode symbols
    # Edit with care
    return string.replace("ゟ", "ヨリ") \
        .translate(HIRA_TO_KATA) \
        .replace("ヷ", "ヷ") \
        .replace("ヸ", "ヸ") \
        .replace("ヹ", "ヹ") \
        .replace("ヺ", "ヺ")

def shin_to_kyu(string: str) -> str:
    return string.translate(SHIN_TO_KYU)

def kyu_to_shin(string: str) -> str:
    return string.translate(KYU_TO_SHIN)

def string_to_ordinals(string: str) -> List[int]:
    return [ord(char) for char in string]

class TestConversion(unittest.TestCase):
    def test_kata_hira(self):
        # XXX: Composite unicode characters are present
        # Edit with care
        plain = [
            ("わ", "ワ"), ("ら", "ラ"), ("や", "ヤ"), ("ま", "マ"), ("は", "ハ"), ("な", "ナ"), ("た", "タ"), ("さ", "サ"), ("か", "カ"), ("あ", "ア"),
            ("ゐ", "ヰ"), ("り", "リ"),               ("み", "ミ"), ("ひ", "ヒ"), ("に", "ニ"), ("ち", "チ"), ("し", "シ"), ("き", "キ"), ("い", "イ"),
            ("ん", "ン"), ("る", "ル"), ("ゆ", "ユ"), ("む", "ム"), ("ふ", "フ"), ("ぬ", "ヌ"), ("つ", "ツ"), ("す", "ス"), ("く", "ク"), ("う", "ウ"),
            ("ゑ", "ヱ"), ("れ", "レ"),               ("め", "メ"), ("へ", "ヘ"), ("ね", "ネ"), ("て", "テ"), ("せ", "セ"), ("け", "ケ"), ("え", "エ"),
            ("を", "ヲ"), ("ろ", "ロ"), ("よ", "ヨ"), ("も", "モ"), ("ほ", "ホ"), ("の", "ノ"), ("と", "ト"), ("そ", "ソ"), ("こ", "コ"), ("お", "オ"),
        ]
        dakuten = [
            ("わ゙", "ヷ"), ("ば", "バ"), ("だ", "ダ"), ("ざ", "ザ"), ("が", "ガ"), ("あ゙", "ア゙"),
            ("ゐ゙", "ヸ"), ("び", "ビ"), ("ぢ", "ヂ"), ("じ", "ジ"), ("ぎ", "ギ"),
            ("ゔ", "ヴ"), ("ぶ", "ブ"), ("づ", "ヅ"), ("ず", "ズ"), ("ぐ", "グ"),
            ("ゑ゙", "ヹ"), ("べ", "ベ"), ("で", "デ"), ("ぜ", "ゼ"), ("げ", "ゲ"),
            ("を゙", "ヺ"), ("ぼ", "ボ"), ("ど", "ド"), ("ぞ", "ゾ"), ("ご", "ゴ"),
        ]
        handakuten = [
            ("ら゚", "ラ゚"), ("ぱ", "パ"), ("た゚", "タ゚"), ("さ゚", "サ゚"), ("か゚", "カ゚"), ("あ゚", "ア゚"),
            ("り゚", "リ゚"), ("ぴ", "ピ"), ("ち゚", "チ゚"), ("し゚", "シ゚"), ("き゚", "キ゚"), ("い゚", "イ゚"),
            ("る゚", "ル゚"), ("ぷ", "プ"), ("つ゚", "ツ゚"), ("す゚", "ス゚"), ("く゚", "ク゚"), ("う゚", "ウ゚"),
            ("れ゚", "レ゚"), ("ぺ", "ペ"), ("て゚", "テ゚"), ("せ゚", "セ゚"), ("け゚", "ケ゚"), ("え゚", "エ゚"),
            ("ろ゚", "ロ゚"), ("ぽ", "ポ"), ("と゚", "ト゚"), ("そ゚", "ソ゚"), ("こ゚", "コ゚"), ("お゚", "オ゚"),
        ]

        for pairs in [plain, dakuten, handakuten]:
            for pair in pairs:
                hira, kata = pair[0], pair[1]
                self.assertEqual(kata_to_hira(kata), hira)
                self.assertEqual(hira_to_kata(hira), kata)

    def test_shin_kyu(self):
        self.assertEqual(shin_to_kyu("旧字体"), "舊字體")
        self.assertEqual(kyu_to_shin("舊字體"), "旧字体")
