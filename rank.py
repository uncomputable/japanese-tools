from dataclasses import dataclass
from typing import List, Any, Dict, Optional, Iterator, Callable
import unittest

import bccwj
from definition import DictionaryWriter, DictionaryReader
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
    def from_json(cls, obj: List[Any]) -> "Rank":
        text, reading, rank = obj
        return Rank(Term(text, reading), rank)

    def to_json(self) -> List[Any]:
        return [
            self.term.text,
            self.term.reading,
            self.rank
        ]


class TestRank(unittest.TestCase):
    def test_impl(self):
        a = Rank(Term("ア", "あ"), 0)
        b = Rank(Term("ア", "あ"), 1)

        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))


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


class RankDictionaryReader(DictionaryReader):
    term_bank_name = "term_meta_bank"
    datum_class = Rank


class RankDictionaryWriter(DictionaryWriter):
    is_sequenced = False
    term_bank_name = "term_meta_bank"
    frequency_mode = "rank-based"


class TestRankDictionary(unittest.TestCase):
    def test_write(self):
        bag = bccwj.read_bag("BCCWJ_frequencylist_suw_ver1_1.tsv")
        it = from_counts(bag.to_counts())
        it = below_max_rank(it, 80000)
        it = copy_term(it, Term.update_kanji_repetition_marks)
        data = list(it)
        RankDictionaryWriter(data) \
            .with_title("BCCWJ") \
            .with_revision("超銀河版") \
            .with_author("グレン団") \
            .with_path("bccwj.zip") \
            .in_chunks(10000) \
            .write()
