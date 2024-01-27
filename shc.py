import os
import unittest
from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

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

def read_bag(zip_dir_path: str) -> OccurrenceBag:
    return read_suw_bag(zip_dir_path)


class TestSHC(unittest.TestCase):
    def test_read_suw(self):
        bag = read_suw_bag("../data")
        self.assertEqual(128808, len(bag))
