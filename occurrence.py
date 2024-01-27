from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict
from zipfile import ZipFile
import unittest

import conversion
from term import Term


@dataclass(frozen=True)
class Occurrence:
    """
    Occurrence of a term in a textual source.

    Instances of this class are immutable.
    """
    term: Term
    """
    The term itself.
    """
    provenance: str
    """
    Source in which the term occurred.
    """

    def __repr__(self) -> str:
        return f"{self.term}@{self.provenance}"


class TestOccurrence(unittest.TestCase):
    def test_impl(self):
        a = Occurrence(Term("ア", "あ"), "ある出所")
        b = Occurrence(Term("ア", "あ"), "違う出所")

        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))


class OccurrenceBag:
    data: Dict[Term, Dict[str, int]]
    """
    Maps occurrences to their count.

    Terms are mapped to their sources.
    Sources are in turn mapped to the term count.
    """

    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(int))

    def insert(self, occurrence: Occurrence, count: int):
        self.data[occurrence.term][occurrence.provenance] += count

    def get(self, occurrence: Occurrence) -> int:
        return self.data[occurrence.term][occurrence.provenance]

    def __len__(self) -> int:
        return len(self.data)

    def extend_overlap(self, other: "OccurrenceBag"):
        """
        Conservatively add counts from another bag.

        Assume that textual sources of both bags overlap.
        For each term and source, take the maximum count from either bag.

        Counts too few occurrences if textual sources are actually distinct.
        """
        for term in other.data:
            for source in other.data[term]:
                total_count = max(self.data[term][source], other.data[term][source])
                self.data[term][source] = total_count

    def extend_distinct(self, other: "OccurrenceBag"):
        """
        Boldly add counts from another bag.

        Assume that textual sources of both bags are distinct.
        For each term and source, take the sum the counts of both bags.

        Counts too many occurrences if textual sources actually overlap.
        """
        for term in other.data:
            for source in other.data[term]:
                total_count = self.data[term][source] + other.data[term][source]
                self.data[term][source] = total_count

    def to_counts(self) -> Dict[Term, int]:
        counts: Dict[Term, int] = defaultdict(int)
        for term in self.data:
            for n in self.data[term].values():
                counts[term] += n
        return counts


class OccurrenceReader:
    zip_path: Optional[str] = None
    paths: List[str]
    separator: Optional[str] = None
    text_index: Optional[int] = None
    reading_index: Optional[int] = None
    count_index: Optional[int] = None
    provenance_indices: List[int]
    skip_lines: int
    encoding: str

    def __init__(self):
        self.paths = []
        self.provenance_indices = []
        self.skip_lines = 0
        self.encoding = "utf-8"

    def with_zip_path(self, zip_path: str) -> "OccurrenceReader":
        self.zip_path = zip_path
        return self

    def add_path(self, path: str) -> "OccurrenceReader":
        self.paths.append(path)
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
        if len(self.paths) == 0:
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

        if self.zip_path is not None:
            with ZipFile(self.zip_path, mode="r") as zip_file:
                for path in self.paths:
                    with zip_file.open(path, "r") as f:
                        content = f.read().decode(self.encoding)
                        self.update_bag(content, bag)
        else:
            for path in self.paths:
                with open(path, "r", encoding=self.encoding) as f:
                    content = f.read()
                    self.update_bag(content, bag)

        return bag

    def update_bag(self, content: str, bag: OccurrenceBag):
        assert self.text_index is not None
        assert self.reading_index is not None
        assert self.count_index is not None

        for (line_index, line) in enumerate(content.splitlines()):
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


class TestOccurrenceBag(unittest.TestCase):
    def test_read(self):
        occurrences = OccurrenceReader() \
            .with_zip_path("../data/BCCWJ_frequencylist_suw_ver1_1.zip") \
            .add_path("BCCWJ_frequencylist_suw_ver1_1.tsv") \
            .with_separator("\t") \
            .with_skip_lines(1) \
            .with_text_index(2) \
            .with_reading_index(1) \
            .with_count_index(6) \
            .read()
        self.assertEqual(175634, len(occurrences))

    def test_extend_overlap(self):
        a = OccurrenceBag()
        a.insert(Occurrence(Term("ア", "あ"), "ある出所"), 10)
        a.insert(Occurrence(Term("イ", "い"), "ある出所"), 5)

        b = OccurrenceBag()
        b.insert(Occurrence(Term("ア", "あ"), "ある出所"), 5)
        b.insert(Occurrence(Term("ア", "あ"), "違う出所"), 5)

        a.extend_overlap(b)
        self.assertEqual(a.get(Occurrence(Term("ア", "あ"), "ある出所")), 10)
        self.assertEqual(a.get(Occurrence(Term("ア", "あ"), "違う出所")), 5)
        self.assertEqual(a.get(Occurrence(Term("イ", "い"), "ある出所")), 5)

    def test_to_counts(self):
        a = OccurrenceBag()
        a.insert(Occurrence(Term("ア", "あ"), "ある出所"), 10)
        a.insert(Occurrence(Term("ア", "あ"), "違う出所"), 5)
        a.insert(Occurrence(Term("イ", "い"), "ある出所"), 5)

        counts = a.to_counts()
        self.assertEqual(counts.get(Term("ア", "あ")), 15)
        self.assertEqual(counts.get(Term("イ", "い")), 5)
