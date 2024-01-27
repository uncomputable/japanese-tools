import os
import unittest
from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

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

def read_bag(zip_dir_path: str) -> OccurrenceBag:
    return read_suw_bag(zip_dir_path)


class TestCSJ(unittest.TestCase):
    def test_read_suw(self):
        bag = read_suw_bag("../data")
        self.assertEqual(41488, len(bag))
