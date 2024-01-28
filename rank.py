import argparse
import json
from dataclasses import dataclass
from datetime import date
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

    def test_from_json(self):
        rank = Rank(Term("ア", "ア"), 0)
        serializations = [
            '["ア","freq",0]',
            '["ア","freq",{"value":0}]',
            '["ア","freq",{"value":0,"displayValue":"zero"}]',
            '["ア","freq",{"frequency":0}]',  # illegal by schema, but occurs in the wild
            '["ア","freq",{"reading":"ア","frequency":0}]',
            '["ア","freq",{"reading":"ア","frequency":{"value":0}}]',
            '["ア","freq",{"reading":"ア","frequency":{"value":0,"displayValue":"zero"}}]',
        ]

        for s in serializations:
            obj = json.loads(s)
            self.assertEqual(rank, Rank.from_json(obj))

    def test_json_roundtrip(self):
        rank = Rank(Term("ア", "あ"), 0)
        s = rank.to_json()
        self.assertEqual(rank, Rank.from_json(s))

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert frequency dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to input dictionary")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("--max", type=int, default=80000, help="Maximum term frequency in output")

    args = parser.parse_args()

    dic = Rank.dictionary_reader() \
        .with_path(args.path_in) \
        .read()

    it = iter(dic)
    it = below_max_rank(it, args.max)
    it = copy_term(it, Term.update_kanji_repetition_marks)

    dic \
        .with_data_same_type(list(it)) \
        .with_revision(f"{dic.revision} converted {date.today().isoformat()}") \
        .writer() \
        .with_path(args.path_out) \
        .write()
