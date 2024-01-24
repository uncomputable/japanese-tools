from typing import Iterator, Dict, Tuple, Callable, Optional

from definition import Definition
from term import Term

def definitions_and_counts(it: Iterator[Definition], counts: Dict[Term, int]) -> Iterator[Tuple[Definition, int]]:
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
