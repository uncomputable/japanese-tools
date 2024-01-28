import json
from dataclasses import dataclass
from typing import List, Any, Dict, Optional, Iterator, Callable
import unittest

from dictionary import Dictionary, DictionaryReader
from term import Term


@dataclass(frozen=True)
class Rank:
    """
    Rank of a term in terms of count.

    Instances of this class are immutable.
    """
    term: Term
    """
    The term itself.
    """
    rank: int
    """
    Term rank.
    """

    def __repr__(self) -> str:
        return f"{self.term}#{self.rank}"

    @classmethod
    def from_json(cls, obj: Any) -> "Rank":
        text, mode, second_obj = obj
        assert isinstance(text, str)
        assert mode == "freq"

        def parse_frequency(obj_: Any) -> int:
            if isinstance(obj_, int):
                return int(obj_)
            elif isinstance(obj_, dict):
                return int(obj_["value"])
            else:
                assert isinstance(obj_, str)
                raise ValueError("Cannot parse frequency in string format")

        if isinstance(second_obj, dict) and "frequency" in second_obj:
            if "reading" in second_obj:
                reading = second_obj["reading"]
            else:
                reading = text
            third_obj = second_obj["frequency"]
            rank = parse_frequency(third_obj)
        else:
            reading = text
            rank = parse_frequency(second_obj)

        return Rank(Term(text, reading), rank)

    def to_json(self) -> Any:
        return [
            self.term.text,
            "freq",
            {
                "reading": self.term.reading,
                "frequency": self.rank,
            },
        ]

    @classmethod
    def dictionary(cls, data: "List[Rank]") -> Dictionary:
        return Dictionary(data, "term_meta_bank") \
            .with_sequenced(False) \
            .with_frequency_mode("rank-based")

    @classmethod
    def dictionary_reader(cls) -> DictionaryReader:
        return DictionaryReader(Rank, "term_meta_bank")


def from_counts(counts: Dict[Term, int]) -> Iterator[Rank]:
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for rank, (term, _count) in enumerate(sorted_counts):
        yield Rank(term, rank)


def below_max_rank(it: Iterator[Rank], max_rank: int) -> Iterator[Rank]:
    for x in it:
        if x.rank < max_rank:
            yield x


def map_term(it: Iterator[Rank], f: Callable[[Term], Term]) -> Iterator[Rank]:
    def helper(x: Rank) -> Rank:
        return Rank(f(x.term), x.rank)

    return map(helper, it)


def copy_term(it: Iterator[Rank], f: Callable[[Term], Optional[Term]]) -> Iterator[Rank]:
    for x in it:
        yield x
        mapped_term = f(x.term)
        if mapped_term is not None:
            yield Rank(mapped_term, x.rank)


class TestRank(unittest.TestCase):
    def test_impl(self):
        a = Rank(Term("ア", "あ"), 0)
        b = Rank(Term("ア", "あ"), 1)

        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))

    def test_read_dictionary(self):
        dic = Rank.dictionary_reader() \
            .with_path("../frequency-dict/BCCWJ.zip") \
            .read()
        self.assertEqual(dic.title, "書き言葉")
        self.assertEqual(len(dic), 80000)

    def test_read_write_dictionary(self):
        Rank.dictionary_reader() \
            .with_path("../frequency-dict/BCCWJ.zip") \
            .read() \
            .with_revision("超銀河版") \
            .with_author("グレン団") \
            .writer() \
            .with_path("bccwj.zip") \
            .in_chunks(10000) \
            .write()
