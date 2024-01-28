import argparse
import os
import unittest
from datetime import date

import rank
from occurrence import OccurrenceBag, OccurrenceReader
from rank import Rank


def read_suw_bag(zip_dir_path: str) -> OccurrenceBag:
    zip_path = os.path.join(zip_dir_path, "CSJ_frequencylist_suw_ver201803.zip")
    return OccurrenceReader() \
        .with_zip_path(zip_path) \
        .add_path("CSJ_frequencylist_suw_ver201803.tsv") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .read()


class TestCSJ(unittest.TestCase):
    def test_read_suw(self):
        bag = read_suw_bag("../data")
        self.assertEqual(41488, len(bag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CSJ frequency dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to directory with CSJ zip file")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency included in dictionary")

    args = parser.parse_args()

    bag = read_suw_bag(args.path_in)
    it = rank.from_counts(bag.to_counts())
    it = rank.below_max_rank(it, args.max)

    Rank.dictionary(list(it)) \
        .with_title("話し言葉") \
        .with_revision(f"data v2018-03 yomi v{date.today().isoformat()} SUW") \
        .with_author("NINJAL, uncomputable") \
        .with_url("https://github.com/uncomputable/japanese-tools") \
        .with_description("""『日本語話し言葉コーパス（CSJ）』は、日本語の自発音声を大量にあつめて多くの研究用情報を付加した話し言葉研究用のデータベースであり、国立国語研究所・ 情報通信研究機構（旧通信総合研究所）・ 東京工業大学 が共同開発した、質・量ともに世界最高水準の話し言葉データベースです。

        https://clrd.ninjal.ac.jp/csj/index.html""") \
        .with_attribution("CC BY-NC-ND 3.0 https://creativecommons.org/licenses/by-nc-nd/3.0/deed.ja") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
