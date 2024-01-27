import os
import unittest
from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

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

def read_bag(zip_dir_path: str) -> OccurrenceBag:
    suw_bag = read_suw_bag(zip_dir_path)
    luw_bag = read_luw2_bag(zip_dir_path)
    if luw_bag is not None:
        luw_bag.extend_overlap(suw_bag)
    return luw_bag


class TestBCCWJ(unittest.TestCase):
    def test_read_suw(self):
        suw_bag = read_suw_bag("../data")
        self.assertEqual(175634, len(suw_bag))

    def test_read_luw2(self):
        luw_bag = read_luw2_bag("../data")
        self.assertEqual(824690, len(luw_bag))
