from dataclasses import dataclass
from functools import total_ordering
from typing import Optional
import re
import unittest

HIRAGANA = re.compile(r"[ぁ-ゖ]")
KATAKANA = re.compile(r"[ァ-ヺ]")
KANJI = re.compile(r"[\u4E00-\u9FFF\u3400-\u4DBF\u20000-\u2A6DF]")

@dataclass(frozen=True)
@total_ordering
class Term:
    """
    Japanese term with reading.

    Instances of this class are immutable.
    """
    text: str
    """
    The text for the term.
    """
    reading: str
    """
    Reading of the term, or an empty string if the reading is the same as the term.
    """

    def __repr__(self) -> str:
        return f"{self.text}[{self.reading}]"

    def __lt__(self, other: "Term") -> bool:
        return (self.reading, self.text) < (other.reading, other.text)

    def with_default_reading(self) -> "Term":
        if not self.reading:
            return Term(self.text, self.text)
        else:
            return self

    def with_kanji_repetition_marks(self) -> "Optional[Term]":
        new_text = add_repetition_marks(self.text, KANJI, "々")
        if "々" in new_text:
            return Term(new_text, self.reading)
        else:
            return None

    def without_kanji_repetition_marks(self) -> "Optional[Term]":
        if "々" in self.text:
            new_text = remove_repetition_marks(self.text, "々")
            return Term(new_text, self.reading)
        else:
            return None


def add_repetition_marks(string: str, pattern: re.Pattern, mark: str) -> str:
    new_string = ""
    prev_char = ""
    for char in string:
        if pattern.match(char) and char == prev_char:
            new_string += mark
        else:
            new_string += char
            prev_char = char
    return new_string


def remove_repetition_marks(string: str, mark: str) -> str:
    new_string = ""
    prev_char = ""
    for char in string:
        if char == mark:
            new_string += prev_char
        else:
            new_string += char
            prev_char = char
    return new_string


class TestTerm(unittest.TestCase):
    def test_repetition_marks(self):
        words = [
            ("時時", "時々", "ときどき"),
            ("刻刻", "刻々", "こくこく"),
            ("明明白白", "明々白々", "めいめいはくはく"),
            ("赤裸裸", "赤裸々", "せきらら"),
            ("代代木", "代々木", "よよぎ"),
            ("複複複線", "複々々線", "ふくふくふくせん"),
            ("小小小支川", "小々々支川", "しょうしょうしょうしせん"),
        ]

        for without_marks, with_marks, reading in words:
            term_without_marks = Term(without_marks, reading)
            term_with_marks = Term(with_marks, reading)
            self.assertEqual(term_without_marks.with_kanji_repetition_marks(), term_with_marks)
            self.assertEqual(term_with_marks.without_kanji_repetition_marks(), term_without_marks)

    def test_impl(self):
        a = Term("ア", "あ")
        i = Term("イ", "い")

        self.assertEqual(a, a)
        self.assertNotEqual(a, i)
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(i))
