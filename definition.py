from dataclasses import dataclass
from typing import Optional, List, Tuple, Any, Type
from zipfile import ZipFile, ZIP_DEFLATED
import json
import unittest

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
        return Definition(
            term,
            self.def_tags,
            self.conjugation,
            self.popularity,
            self.definitions,
            self.sequence_number,
            self.top_tags
        )

    def with_sequence(self, sequence: int) -> "Definition":
        return Definition(
            self.term,
            self.def_tags,
            self.conjugation,
            self.popularity,
            self.definitions,
            sequence,
            self.top_tags
        )

    def with_popularity(self, popularity: int) -> "Definition":
        return Definition(
            self.term,
            self.def_tags,
            self.conjugation,
            popularity,
            self.definitions,
            self.sequence_number,
            self.top_tags
        )

    def add_def_tag(self, tag: str) -> "Definition":
        def_tags = f"{self.def_tags} {tag}" if self.def_tags else tag
        return Definition(
            self.term,
            def_tags,
            self.conjugation,
            self.popularity,
            self.definitions,
            self.sequence_number,
            self.top_tags
        )

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


class TestDefinition(unittest.TestCase):
    def test_impl(self):
        a = Definition(Term("ア", "あ"), "", "", 0, ("ある定義",), 0, "")
        b = Definition(Term("ア", "あ"), "", "", 0, ("違う定義",), 0, "")

        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))


# TODO Read metadata such as title, revision and author?
class DictionaryReader:
    path: str

    term_bank_name: str = "term_bank"
    datum_class: Type[Any] = Definition
    """
    Class type with a from_json method
    """

    def __init__(self):
        self.path = ""

    def with_path(self, path: str) -> "DictionaryReader":
        self.path = path
        return self

    def read(self) -> List[Any]:
        if not self.path:
            raise ValueError("Path required")

        with ZipFile(self.path, mode="r") as zip_file:
            data = list()
            bank_files = [f for f in zip_file.namelist() if self.term_bank_name in f]

            for file in bank_files:
                with zip_file.open(file, "r") as f:
                    array_obj = json.load(f)
                    for definition_obj in array_obj:
                        definition = self.datum_class.from_json(definition_obj)
                        definition.term.with_default_reading()
                        data.append(definition)

            return data


class DictionaryWriter:
    data: List[Any]
    """
    List of values with a to_json method
    """
    title: Optional[str]
    revision: Optional[str]
    author: Optional[str]
    url: Optional[str]
    description: Optional[str]
    attribution: Optional[str]

    path: Optional[str]
    chunk_size: int

    format: int = 3
    is_sequenced: bool = True
    term_bank_name: str = "term_bank"
    frequency_mode: Optional[str] = None

    def __init__(self, data: List[Any]):
        self.data = data
        self.title = None
        self.revision = None
        self.author = None
        self.url = None
        self.description = None
        self.attribution = None

        self.path = None
        self.chunk_size = len(data)

    def with_title(self, title: str) -> "DictionaryWriter":
        self.title = title
        return self

    def with_revision(self, revision: str) -> "DictionaryWriter":
        self.revision = revision
        return self

    def with_author(self, author: str) -> "DictionaryWriter":
        self.author = author
        return self

    def with_url(self, url: str) -> "DictionaryWriter":
        self.url = url
        return self

    def with_description(self, description: str) -> "DictionaryWriter":
        self.description = description
        return self

    def with_attribution(self, attribution: str) -> "DictionaryWriter":
        self.attribution = attribution
        return self

    def with_path(self, path: str) -> "DictionaryWriter":
        self.path = path
        return self

    def in_chunks(self, chunk_size: int) -> "DictionaryWriter":
        self.chunk_size = chunk_size
        return self

    def write(self):
        if self.title is None:
            raise ValueError("Title required")
        if self.revision is None:
            raise ValueError("Revision required")
        if self.path is None:
            raise ValueError("Path required")

        with ZipFile(self.path, mode="w", compresslevel=ZIP_DEFLATED) as zip_file:
            index_obj = {
                "title": self.title,
                "format": self.format,
                "revision": self.revision,
                "sequenced": self.is_sequenced,
            }
            if self.author is not None:
                index_obj["author"] = self.author
            if self.url is not None:
                index_obj["url"] = self.url
            if self.description is not None:
                index_obj["description"] = self.description
            if self.attribution is not None:
                index_obj["attribution"] = self.attribution
            if self.frequency_mode is not None:
                index_obj["frequencyMode"] = self.frequency_mode

            json_str = json.dumps(index_obj, ensure_ascii=False)
            zip_file.writestr("index.json", json_str)

            for i, datum in enumerate(self.data):
                if i % self.chunk_size == 0:
                    if i > 0:
                        j = i // self.chunk_size

                        file_name = f"f{self.term_bank_name}_{j}.json"
                        json_str = json.dumps(array_obj, sort_keys=True, ensure_ascii=False)
                        zip_file.writestr(file_name, json_str)

                    array_obj = list()

                array_obj.append(datum.to_json())


class TestDictionary(unittest.TestCase):
    def test_read(self):
        data = DictionaryReader() \
            .with_path("../self-made-yomichan/新新明解.zip") \
            .read()
        self.assertEquals(82414, len(data))

        for item in data:
            self.assertTrue(item.is_normal())

    def test_read_write(self):
        data = DictionaryReader() \
            .with_path("../self-made-yomichan/新新明解.zip") \
            .read()
        DictionaryWriter(data) \
            .with_title("新新明解") \
            .with_revision("超銀河版") \
            .with_author("グレン団") \
            .with_path("shinmeikai.zip") \
            .in_chunks(10000) \
            .write()
