from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict
import unittest
import conversion

from term import Term


@dataclass
class Occurrence:
    term: Term
    """
    The term itself.
    """
    provenance: str
    """
    Source in which the term occurred.
    """

    def __hash__(self) -> hash:
        return hash((self.term, self.provenance))


class OccurrenceBag:
    data: Dict[Occurrence, int]
    """
    Maps occurrences to their count.
    """

    def __init__(self):
        self.data = defaultdict(int)

    def insert(self, occurrence: Occurrence, count: int):
        self.data[occurrence] += count

    def get(self, occurrence: Occurrence) -> int:
        return self.data[occurrence]

    def __len__(self) -> int:
        return len(self.data)


class OccurrenceReader:
    zip_path: str
    """
    Path to zip file.
    """
    path: str
    """
    Path to plain text file.

    If zip path is nonempty, then this path lives inside the zip file.
    """
    separator: str
    text_index: Optional[int]
    reading_index: Optional[int]
    count_index: Optional[int]
    provenance_indices: List[int]
    skip_lines: int
    encoding: str

    def __init__(self):
        self.zip_path = ""
        self.path = ""
        self.separator = ""
        self.text_index = None
        self.reading_index = None
        self.count_index = None
        self.provenance_indices = []
        self.skip_lines = 0
        self.encoding = "utf-8"

    def with_zip_path(self, zip_path: str) -> "OccurrenceReader":
        self.zip_path = zip_path
        return self

    def with_path(self, path: str) -> "OccurrenceReader":
        self.path = path
        return self

    def with_separator(self, separator: str) -> "OccurrenceReader":
        self.separator = separator
        return self

    def with_text_index(self, text_index: int) -> "OccurrenceReader":
        self.text_index = text_index
        return self

    def with_reading_index(self, reading_index: int) -> "OccurrenceReader":
        self.reading_index = reading_index
        return self

    def with_count_index(self, count_index: int) -> "OccurrenceReader":
        self.count_index = count_index
        return self

    def add_provenance_index(self, provenance_index) -> "OccurrenceReader":
        self.provenance_indices.append(provenance_index)
        return self

    def with_skip_lines(self, skip_lines: int) -> "OccurrenceReader":
        self.skip_lines = skip_lines
        return self

    def with_encoding(self, encoding: str) -> "OccurrenceReader":
        self.encoding = encoding
        return self

    def read(self) -> OccurrenceBag:
        if not self.path:
            raise ValueError("Path required")
        if not self.separator:
            raise ValueError("Separator required")
        if self.text_index is None:
            raise ValueError("Text index required")
        if self.reading_index is None:
            raise ValueError("Reading index required")
        if self.count_index is None:
            raise ValueError("Count index required")

        bag = OccurrenceBag()

        with open(self.path, "r", encoding=self.encoding) as f:
            for (line_index, line) in enumerate(f):
                if line_index < self.skip_lines:
                    continue

                split_line = line.split(self.separator)

                text = split_line[self.text_index]
                reading = conversion.kata_to_hira(split_line[self.reading_index])
                term = Term(text, reading).with_default_reading()
                provenance = ",".join(map(lambda index: split_line[index], self.provenance_indices))
                occurrence = Occurrence(term, provenance)
                count = int(split_line[self.count_index])
                bag.insert(occurrence, count)

        return bag


class TestOccurrenceBag(unittest.TestCase):
    def test_read(self):
        occurrences = OccurrenceReader() \
            .with_path("BCCWJ_frequencylist_suw_ver1_1.tsv") \
            .with_separator("\t") \
            .with_text_index(2) \
            .with_reading_index(1) \
            .with_count_index(6) \
            .read()
        self.assertEqual(175634, len(occurrences))
