import dataclasses
from dataclasses import dataclass
from typing import List, Tuple, Any, Iterator, Dict, Callable, Optional
import unittest

from dictionary import Dictionary, DictionaryReader
from term import Term


@dataclass(frozen=True)
class Definition:
    """
    Definition of a term from a dictionary.

    Instances of this class are immutable.
    """
    term: Term
    """
    The term itself.
    """
    def_tags: str
    """
    String of space-separated tags for the definition.
    
    An empty string is treated as no tags.
    """
    conjugation: str
    """
    String of space-separated rule identifiers for the definition which is used to validate delinflection.
    
    Valid rule identifiers are: v1: ichidan verb; v5: godan verb; vs: suru verb; vk: kuru verb; adj-i: i-adjective.
    An empty string corresponds to words which aren't inflected, such as nouns.
    """
    popularity: int
    """
    Score used to determine popularity.
    
    Negative values are more rare and positive values are more frequent. This score is also used to sort search results.
    """
    definitions: Tuple[str, ...]
    """
    Array of definitions for the term.
    """
    sequence_number: int
    """
    Sequence number for the term.
    
    Terms with the same sequence number can be shown together when the "resultOutputMode" option is set to "merge"
    """
    top_tags: str
    """
    String of space-separated tags for the term.
    
    An empty string is treated as no tags.
    """

    def get_definition(self) -> str:
        return self.definitions[0]

    def with_term(self, term: Term) -> "Definition":
        return dataclasses.replace(self, term=term)

    def with_sequence(self, sequence: int) -> "Definition":
        return dataclasses.replace(self, sequence_number=sequence)

    def with_popularity(self, popularity: int) -> "Definition":
        return dataclasses.replace(self, popularity=popularity)

    def add_def_tag(self, tag: str) -> "Definition":
        def_tags = f"{self.def_tags} {tag}" if self.def_tags else tag
        return dataclasses.replace(self, def_tags=def_tags)

    def is_normal(self) -> bool:
        return self.top_tags == "" and len(self.definitions) == 1

    @classmethod
    def from_json(cls, obj: List[Any]) -> "Definition":
        text, reading, def_tags, conjugation, popularity, definitions, sequence_number, top_tags = obj
        term = Term(text, reading)
        return Definition(term, def_tags, conjugation, popularity, definitions, sequence_number, top_tags)

    def to_json(self) -> List[Any]:
        return [
            self.term.text,
            self.term.reading,
            self.def_tags,
            self.conjugation,
            self.popularity,
            self.definitions,
            self.sequence_number,
            self.top_tags
        ]

    @classmethod
    def dictionary(cls, data: "List[Definition]") -> Dictionary:
        return Dictionary(data, "term_bank") \
            .with_sequenced(True)

    @classmethod
    def dictionary_reader(cls) -> DictionaryReader:
        return DictionaryReader(Definition, "term_bank")


def with_counts(it: Iterator[Definition], counts: Dict[Term, int]) -> Iterator[Tuple[Definition, int]]:
    """
    Iterate over each term definition together with the term's count.

    Iterator[definition] → Iterator[definition + count]
    """
    def helper(x: Definition) -> Tuple[Definition, int]:
        return x, counts.get(x.term, 0)

    return map(helper, it)

def sort_by_count(it: Iterator[Tuple[Definition, int]]) -> Iterator[Tuple[Definition, int]]:
    """
    Iterate in descending order of term counts.

    Iterator[definition + count] → Iterator[definition + count]
    """
    sorted_list = sorted(it, key=lambda x: x[1], reverse=True)
    for item in sorted_list:
        yield item

def count_as_popularity(it: Iterator[Tuple[Definition, int]]) -> Iterator[Tuple[Definition, int]]:
    """
    Set the popularity field of each definition equal to the term count.

    Iterator[definition + count] → Iterator[definition + count]
    """
    def helper(x: Tuple[Definition, int]) -> Tuple[Definition, int]:
        return x[0].with_popularity(x[1]), x[1]

    return map(helper, it)

def only_definitions(it: Iterator[Tuple[Definition, int]]) -> Iterator[Definition]:
    """
    Iterate over definitions only.

    Iterator[definition + count] → Iterator[definition]
    """
    return map(lambda x: x[0], it)

def sort_by_term(it: Iterator[Definition]) -> Iterator[Definition]:
    """
    Iterate in ascending order of terms (lexicographic order).

    Iterator[definition] → Iterator[definition]
    """
    sorted_list = sorted(it, key=lambda x: x.term)
    for item in sorted_list:
        yield item

def position_as_sequence(it: Iterator[Definition]) -> Iterator[Definition]:
    """
    Set the sequence field of each definition equal to the iterator position.

    The first definition is assigned sequence zero.
    The second definition is assigned sequence one.
    And so on.

    Iterator[definition] → Iterator[definition]
    """
    def helper(x: Tuple[int, Definition]) -> Definition:
        return x[1].with_sequence(x[0])

    return map(helper, enumerate(it))

def map_term(it: Iterator[Definition], f: Callable[[Term], Term]) -> Iterator[Definition]:
    """
    Set the term field of each definition equal to the result of function f.

    Function f is evaluated on the content of the term field.

    Iterator[definition] → Iterator[definition]
    """
    def helper(x: Definition) -> Definition:
        return x.with_term(f(x.term))

    return map(helper, it)

def copy_term(it: Iterator[Definition], f: Callable[[Term], Optional[Term]]) -> Iterator[Definition]:
    """
    Create a copy of each definition where the term field is equal the result of function f.
    The original definition is preserved.

    Function f is evaluated on the content of the term field.
    If function f returns None then no copy is produced.

    Iterator[definition] → Iterator[definition]
    """
    for x in it:
        yield x
        mapped_term = f(x.term)
        if mapped_term is not None:
            yield x.with_term(mapped_term)

def add_def_tag(it: Iterator[Definition], f: Callable[[Definition], Optional[str]]) -> Iterator[Definition]:
    """
    Add the result of function f to the def tag field of each definition.

    Function f is evaluated on the whole definition.
    If function f returns None then the definition stays unchanged.

    Iterator[definition] → Iterator[definition]
    """
    for x in it:
        tag = f(x)
        if tag is not None:
            yield x.add_def_tag(tag)
        else:
            yield x


class TestDefinition(unittest.TestCase):
    def test_impl(self):
        a = Definition(Term("ア", "あ"), "", "", 0, ("ある定義",), 0, "")
        b = Definition(Term("ア", "あ"), "", "", 0, ("違う定義",), 0, "")

        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))

    def test_read_dictionary(self):
        dic = Definition.dictionary_reader() \
            .with_path("../self-made-yomichan/新新明解.zip") \
            .read()
        self.assertEqual(dic.title, "新明解国語辞典 第五版")
        self.assertEqual(len(dic), 82414)

        for item in dic:
            self.assertTrue(item.is_normal())

    def test_read_write_dictionary(self):
        Definition.dictionary_reader() \
            .with_path("../self-made-yomichan/新新明解.zip") \
            .read() \
            .with_revision("超銀河版") \
            .with_author("グレン団") \
            .writer() \
            .with_path("shinmeikai.zip") \
            .in_chunks(10000) \
            .write()
