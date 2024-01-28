import argparse
import os
from datetime import date
from typing import Optional

import bccwj
import definition
import jlpt
from definition import Definition
from dictionary import Dictionary
from term import Term


def read_dictionary(zip_dir_path: str) -> Dictionary:
    zip_path = os.path.join(zip_dir_path, "新明解国語辞典第五版v3.zip")
    return Definition.dictionary_reader() \
        .with_path(zip_path) \
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
    parser = argparse.ArgumentParser(description="Upgrade Shinmeikai dictionary for Yomichan")

    parser.add_argument("path_in", type=str, help="Path to directory with Shinmeikai dictionary")
    parser.add_argument("path_out", type=str, help="Path of output dictionary")
    parser.add_argument("path_bccwj", type=str, help="Path to directory with BCCWJ zip files")

    args = parser.parse_args()

    dic = read_dictionary(args.path_in)
    bag, includes_luw = bccwj.read_bag(args.path_bccwj)
    counts = bag.to_counts()

    it = iter(dic)
    it = definition.with_counts(it, counts)
    it = definition.sort_by_count(it)
    it = definition.count_as_popularity(it)
    it = definition.only_definitions(it)
    it = definition.position_as_sequence(it)
    it = definition.sort_by_term(it)
    it = definition.copy_term(it, Term.update_kanji_repetition_marks)
    it = definition.add_def_tag(it, tag_importance)
    it = definition.add_def_tag(it, jlpt.tag_level)
    it = definition.map_term(it, remove_stars)

    Definition.dictionary(list(it)) \
        .with_title("新明解国語辞典") \
        .with_revision(f"data v1997-11-03 yomi v{date.today().isoformat()}") \
        .with_author("Yoga, uncomputable") \
        .writer() \
        .with_path(args.path_out) \
        .in_chunks(10000) \
        .write()
