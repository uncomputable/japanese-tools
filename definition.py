import dataclasses
from dataclasses import dataclass
from typing import List, Tuple, Any
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
