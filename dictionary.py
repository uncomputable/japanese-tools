import dataclasses
from dataclasses import dataclass
from typing import Optional, List, Any, Type, Iterator, Dict
from zipfile import ZipFile, ZIP_DEFLATED
import json


@dataclass(frozen=True)
class Dictionary:
    data: List[Any]
    term_bank_name: str
    title: Optional[str] = None
    revision: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    attribution: Optional[str] = None
    sequenced: Optional[bool] = None
    frequency_mode: Optional[str] = None

    def __iter__(self) -> Iterator[Any]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def with_title(self, title: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, title=title)

    def with_revision(self, revision: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, revision=revision)

    def with_author(self, author: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, author=author)

    def with_url(self, url: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, url=url)

    def with_description(self, description: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, description=description)

    def with_attribution(self, attribution: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, attribution=attribution)

    def with_sequenced(self, sequenced: Optional[bool]) -> "Dictionary":
        return dataclasses.replace(self, sequenced=sequenced)

    def with_frequency_mode(self, frequency_mode: Optional[str]) -> "Dictionary":
        return dataclasses.replace(self, frequency_mode=frequency_mode)

    def with_index_json(self, obj: Dict[str, Any]) -> "Dictionary":
        return self \
            .with_title(obj.get("title")) \
            .with_revision(obj.get("revision")) \
            .with_author(obj.get("author")) \
            .with_url(obj.get("url")) \
            .with_description(obj.get("description")) \
            .with_attribution(obj.get("attribution")) \
            .with_sequenced(obj.get("sequenced")) \
            .with_frequency_mode(obj.get("frequencyMode"))

    def to_index_json(self) -> Dict[str, Any]:
        index_obj = {
            "format": 3,
            "title": self.title,
            "revision": self.revision,
            "author": self.author,
            "url": self.url,
            "description": self.description,
            "attribution": self.attribution,
            "sequenced": self.sequenced,
            "frequencyMode": self.frequency_mode,
        }
        return {k: v for k, v in index_obj.items() if v is not None}

    def writer(self) -> "DictionaryWriter":
        return DictionaryWriter(self)


class DictionaryReader:
    data_class: Type[Any]
    term_bank_name: str
    path: Optional[str]

    def __init__(self, data_class: Type[Any], term_bank_name: str):
        self.data_class = data_class
        self.term_bank_name = term_bank_name
        self.path = None

    def with_path(self, path: str) -> "DictionaryReader":
        self.path = path
        return self

    def read(self) -> Dictionary:
        if self.path is None:
            raise ValueError("Path required")

        with ZipFile(self.path, mode="r") as zip_file:
            data = list()
            bank_files = [f for f in zip_file.namelist() if self.term_bank_name in f]

            for file in bank_files:
                with zip_file.open(file, "r") as f:
                    array_obj = json.load(f)
                    for data_obj in array_obj:
                        datum = self.data_class.from_json(data_obj)
                        datum.term.with_default_reading()
                        data.append(datum)

            with zip_file.open("index.json", "r") as f:
                index_obj = json.load(f)
                dictionary = Dictionary(data, self.term_bank_name) \
                        .with_index_json(index_obj)

            return dictionary


class DictionaryWriter:
    dictionary: Dictionary
    path: Optional[str]
    chunk_size: int

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary
        self.path = None
        self.chunk_size = len(self.dictionary)

    def with_path(self, path: str) -> "DictionaryWriter":
        self.path = path
        return self

    def in_chunks(self, chunk_size: int) -> "DictionaryWriter":
        self.chunk_size = chunk_size
        return self

    def write(self):
        if self.path is None:
            raise ValueError("Path required")

        with ZipFile(self.path, mode="w", compresslevel=ZIP_DEFLATED) as zip_file:
            index_obj = self.dictionary.to_index_json()
            json_str = json.dumps(index_obj, ensure_ascii=False)
            zip_file.writestr("index.json", json_str)

            for chunk_index, data_index in enumerate(range(0, len(self.dictionary), self.chunk_size)):
                chunk = self.dictionary.data[data_index:data_index + self.chunk_size]
                chunk_obj = [x.to_json() for x in chunk]
                file_name = f"{self.dictionary.term_bank_name}_{chunk_index}.json"
                json_str = json.dumps(chunk_obj, sort_keys=True, ensure_ascii=False)
                zip_file.writestr(file_name, json_str)
