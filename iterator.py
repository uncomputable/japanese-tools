from typing import Iterator, Dict, Tuple, Callable, Optional

from definition import Definition
from term import Term

def definitions_and_counts(it: Iterator[Definition], counts: Dict[Term, int]) -> Iterator[Tuple[Definition, int]]:
    def helper(x: Definition) -> Tuple[Definition, int]:
        return x, counts.get(x.term, 0)

    return map(helper, it)

def sort_by_count(it: Iterator[Tuple[Definition, int]]) -> Iterator[Tuple[Definition, int]]:
    sorted_list = sorted(it, key=lambda x: x[1], reverse=True)
    for item in sorted_list:
        yield item

def count_as_popularity(it: Iterator[Tuple[Definition, int]]) -> Iterator[Tuple[Definition, int]]:
    def helper(x: Tuple[Definition, int]) -> Tuple[Definition, int]:
        return x[0].with_popularity(x[1]), x[1]

    return map(helper, it)

def only_definitions(it: Iterator[Tuple[Definition, int]]) -> Iterator[Definition]:
    return map(lambda x: x[0], it)

def sort_by_term(it: Iterator[Definition]) -> Iterator[Definition]:
    sorted_list = sorted(it, key=lambda x: x.term)
    for item in sorted_list:
        yield item

def position_as_sequence(it: Iterator[Definition]) -> Iterator[Definition]:
    def helper(x: Tuple[int, Definition]) -> Definition:
        return x[1].with_sequence(x[0])

    return map(helper, enumerate(it))

def map_term(it: Iterator[Definition], f: Callable[[Term], Term]) -> Iterator[Definition]:
    def helper(x: Definition) -> Definition:
        return x.with_term(f(x.term))

    return map(helper, it)

def copy_term(it: Iterator[Definition], f: Callable[[Term], Optional[Term]]) -> Iterator[Definition]:
    for x in it:
        yield x
        mapped_term = f(x.term)
        if mapped_term is not None:
            yield x.with_term(mapped_term)

def add_def_tag(it: Iterator[Definition], f: Callable[[Definition], Optional[str]]) -> Iterator[Definition]:
    for x in it:
        tag = f(x)
        if tag is not None:
            yield x.add_def_tag(tag)
        else:
            yield x
