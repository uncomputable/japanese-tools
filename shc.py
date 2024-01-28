import argparse
import os
import unittest
from datetime import date

import rank
from occurrence import OccurrenceBag, OccurrenceReader
from rank import Rank


def read_suw_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "SHC-LEX_SUW_202305.zip")
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("SHC-LEX_SUW_202305_book.csv") \
        .add_path("SHC-LEX_SUW_202305_magazine.csv") \
        .add_path("SHC-LEX_SUW_202305_newspaper.csv") \
        .with_encoding("utf-16") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(1) \
        .with_reading_index(0) \
        .with_count_index(15) \
        .read()


class TestSHC(unittest.TestCase):
    def test_read_suw(self):
        bag = read_suw_bag("../data")
        self.assertEqual(128808, len(bag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SHC frequency dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to directory with SHC zip file")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency included in dictionary")

    args = parser.parse_args()

    bag = read_suw_bag(args.path_in)
    it = rank.from_counts(bag.to_counts())
    it = rank.below_max_rank(it, args.max)

    Rank.dictionary(list(it)) \
        .with_title("昭和〜平成") \
        .with_revision(f"data v2023-05 yomi v{date.today().isoformat()} SUW") \
        .with_author("NINJAL, uncomputable") \
        .with_url("https://github.com/uncomputable/japanese-tools") \
        .with_description("""『昭和・平成書き言葉コーパス』は、昭和・平成期の日本語を通時的に研究できるように設計したコーパスです。

        雑誌、ベストセラー書籍、新聞

        https://clrd.ninjal.ac.jp/shc/index.html""") \
        .with_attribution("CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
