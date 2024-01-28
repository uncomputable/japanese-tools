import argparse
import os
import unittest
from datetime import date

import rank
from occurrence import OccurrenceBag, OccurrenceReader
from rank import Rank


def read_suw_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "NWJC_frequencylist_suw_ver2022_02.zip")
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("NWJC_frequencylist_suw_ver2022_02/NWJC_frequencylist_suw_ver2022_02.tsv") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .read()


class TestNWJC(unittest.TestCase):
    def test_read_suw(self):
        bag = read_suw_bag("../data")
        self.assertEqual(103931, len(bag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate NWJC frequency dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to directory with NWJC zip file")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency included in dictionary")

    args = parser.parse_args()

    bag = read_suw_bag(args.path_in)
    it = rank.from_counts(bag.to_counts())
    it = rank.below_max_rank(it, args.max)

    Rank.dictionary(list(it)) \
        .with_title("ウェブ") \
        .with_revision(f"data v2022-02 yomi v{date.today().isoformat()} SUW") \
        .with_author("NINJAL, uncomputable") \
        .with_url("https://github.com/uncomputable/japanese-tools") \
        .with_description("""『国語研日本語ウェブコーパス（NWJC）』はウェブを母集団として100億語規模を目標として構築した日本語コーパスです。

        https://masayu-a.github.io/NWJC/""") \
        .with_attribution("CC BY 4.0 https://creativecommons.org/licenses/by/4.0/deed.ja") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
