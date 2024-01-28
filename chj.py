import argparse
import os
import unittest
from datetime import date

import rank
from occurrence import OccurrenceBag, OccurrenceReader
from rank import Rank


def read_modern_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "CHJ_integratedFequencyList_202303.zip")
    # Provenance: 作品名, 部, 本文種別
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("CHJ-LEX_SUW_2023.3_modern_nonmag.csv") \
        .add_path("CHJ-LEX_SUW_2023.3_modern_mag.csv") \
        .with_encoding("utf-16") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(1) \
        .with_reading_index(0) \
        .with_count_index(16) \
        .add_provenance_index(9) \
        .add_provenance_index(10) \
        .add_provenance_index(13) \
        .read()

def read_premodern_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "CHJ_integratedFequencyList_202303.zip")
    # Provenance: 作品名, 部, 本文種別
    suw_bag = OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("CHJ-LEX_SUW_2023.3_premodern.csv") \
        .with_encoding("utf-16") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(1) \
        .with_reading_index(0) \
        .with_count_index(16) \
        .add_provenance_index(9) \
        .add_provenance_index(10) \
        .add_provenance_index(13) \
        .read()
    # Provenance: 作品名, 部, 本文種別
    luw_bag = OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("CHJ-LEX_LUW_2023.3.csv") \
        .with_encoding("utf-16") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(1) \
        .with_reading_index(0) \
        .with_count_index(13) \
        .add_provenance_index(8) \
        .add_provenance_index(9) \
        .add_provenance_index(12) \
        .read()
    luw_bag.extend_overlap(suw_bag)
    return luw_bag


class TestCHJ(unittest.TestCase):
    def test_read_modern(self):
        bag = read_modern_bag("../data")
        self.assertEqual(120109, len(bag))

    def test_read_premodern(self):
        bag = read_premodern_bag("../data")
        self.assertEqual(104284, len(bag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CHJ frequency dictionary")
    parser.add_argument("path_in", type=str, help="Path to directory with CHJ zip file")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency included in dictionary")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--modern", action="store_true", help="Use modern part")
    group.add_argument("--premodern", action="store_false", dest="modern", help="Use premodern part")

    args = parser.parse_args()

    if args.modern:
        bag = read_modern_bag(args.path_in)
        title = "明治〜大正"
        suw_luw_version = "SUW"
        description = """ 『日本語歴史コーパス（CHJ）』は、デジタル時代における日本語史研究の基礎資料として開発を進めているコーパスです。

        明治・大正編：雑誌／教科書／明治初期口語資料／近代小説／新聞／落語SP盤

        https://clrd.ninjal.ac.jp/chj/index.html"""
    else:
        bag = read_premodern_bag(args.path_in)
        title = "奈良〜江戸"
        suw_luw_version = "SUW+LUW"
        description = """『日本語歴史コーパス（CHJ）』は、デジタル時代における日本語史研究の基礎資料として開発を進めているコーパスです。

        奈良時代編：万葉集／宣命／祝詞
        平安時代編：仮名文学／訓点資料
        鎌倉時代編：説話・随筆／日記・紀行／軍記
        室町時代編：狂言／キリシタン資料
        江戸時代編：洒落本／人情本／近松浄瑠璃／随筆・紀行

        https://clrd.ninjal.ac.jp/chj/index.html"""

    it = rank.from_counts(bag.to_counts())
    it = rank.below_max_rank(it, args.max)

    Rank.dictionary(list(it)) \
        .with_title(title) \
        .with_revision(f"data v2023-03 yomi yomi v{date.today().isoformat()} {suw_luw_version}") \
        .with_author("NINJAL, uncomputable") \
        .with_url("https://github.com/uncomputable/japanese-tools") \
        .with_description(description) \
        .with_attribution("CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
