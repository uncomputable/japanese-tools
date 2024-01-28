import argparse
import os
import unittest
from datetime import date
from typing import Optional, Tuple

import rank
from occurrence import OccurrenceBag, OccurrenceReader
from rank import Rank


def read_suw_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "BCCWJ_frequencylist_suw_ver1_1.zip")
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("BCCWJ_frequencylist_suw_ver1_1.tsv") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .read()

def read_luw2_bag(zip_dir_path: str) -> Optional[OccurrenceBag]:
    zip_path = os.path.join(zip_dir_path, "BCCWJ_frequencylist_luw2_ver1_1.zip")
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("BCCWJ_frequencylist_luw2_ver1_1.tsv") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .maybe_read()

def read_bag(zip_dir_path: str) -> Tuple[OccurrenceBag, bool]:
    suw_bag = read_suw_bag(zip_dir_path)
    luw_bag = read_luw2_bag(zip_dir_path)
    if luw_bag is None:
        return suw_bag, False
    else:
        luw_bag.extend_overlap(suw_bag)
        return luw_bag, True


class TestBCCWJ(unittest.TestCase):
    def test_read_suw(self):
        suw_bag = read_suw_bag("../data")
        self.assertEqual(175634, len(suw_bag))

    def test_read_luw2(self):
        luw_bag = read_luw2_bag("../data")
        self.assertEqual(824690, len(luw_bag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate BCCWJ frequency dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to directory with BCCWJ zip files")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency included in dictionary")

    args = parser.parse_args()

    bag, includes_luw = read_bag(args.path_in)
    it = rank.from_counts(bag.to_counts())
    it = rank.below_max_rank(it, args.max)
    suw_luw_version = "SUW+LUW" if includes_luw else "SUW"

    Rank.dictionary(list(it)) \
        .with_title("書き言葉") \
        .with_revision(f"data v1.1 (2017-12) yomi v{date.today().isoformat()} {suw_luw_version}") \
        .with_author("NINJAL, uncomputable") \
        .with_url("https://github.com/uncomputable/japanese-tools") \
        .with_description("""『現代日本語書き言葉均衡コーパス（BCCWJ）』は、現代日本語の書き言葉の全体像を把握するために構築したコーパスであり、現在、日本語について入手可能な唯一の均衡コーパスです。

        https://clrd.ninjal.ac.jp/bccwj/index.html""") \
        .with_attribution("CC BY-NC-ND 3.0 https://creativecommons.org/licenses/by-nc-nd/3.0/deed.ja") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
