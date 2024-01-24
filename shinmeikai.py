import argparse
from datetime import datetime
from typing import Optional, List

import bccwj
import iterator
import jlpt
from definition import DictionaryReader, Definition, DictionaryWriter
from term import Term

def read_dictionary(path: str) -> List[Definition]:
    return DictionaryReader() \
        .with_path(path) \
        .read()

def tag_importance(definition: Definition) -> Optional[str]:
    if "⁑" in definition.get_definition():
        return "最重要語"
    if "⁎" in definition.get_definition():
        return "重要語"
    else:
        return None

def remove_stars(term: Term) -> Term:
    text = term.text
    reading = term.reading

    if "⁑" in text:
        text = text.replace("⁑", "")
    if "⁑" in reading:
        reading = reading.replace("⁑", "")
    if "⁎" in text:
        text = text.replace("⁎", "")
    if "⁎" in reading:
        reading = reading.replace("⁎", "")

    return Term(text, reading)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade 新明解国語辞典")

    parser.add_argument("path_in", type=str, help="Path to input dictionary")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("path_suw", type=str, help="Path to BCCWJ_frequencylist_suw_ver1_1.tsv")
    parser.add_argument("path_luw", nargs="?", type=str, help="Path to BCCWJ_frequencylist_luw2_ver1_1.tsv")

    args = parser.parse_args()

    data = read_dictionary(args.path_in)
    bag = bccwj.read_bag(args.path_suw, args.path_luw)
    counts = bag.to_counts()

    it = iter(data)
    it = iterator.definitions_and_counts(it, counts)
    it = iterator.sort_by_count(it)
    it = iterator.count_as_popularity(it)
    it = iterator.only_definitions(it)
    it = iterator.position_as_sequence(it)
    it = iterator.sort_by_term(it)
    it = iterator.copy_term(it, Term.update_kanji_repetition_marks)
    it = iterator.add_def_tag(it, tag_importance)
    it = iterator.add_def_tag(it, jlpt.tag_level)
    it = iterator.map_term(it, remove_stars)

    new_data = list(it)
    DictionaryWriter(new_data) \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .with_title("新明解国語辞典") \
        .with_revision(f"次元突破版{datetime.today().isoformat()}") \
        .with_author("Yoga, uncomputable") \
        .write()
