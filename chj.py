import os
import unittest
from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

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
