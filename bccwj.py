from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

def read_bag(zip_path_suw: str, zip_path_luw: Optional[str] = None) -> OccurrenceBag:
    bag = OccurrenceReader() \
        .with_zip_path(zip_path_suw) \
        .add_path("BCCWJ_frequencylist_suw_ver1_1.tsv") \
        .with_separator("\t") \
        .with_skip_lines(1) \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .read()
    if zip_path_luw:
        other = OccurrenceReader() \
            .with_zip_path(zip_path_luw) \
            .add_path("BCCWJ_frequencylist_luw2_ver1_1.tsv") \
            .with_separator("\t") \
            .with_skip_lines(1) \
            .with_text_index(2) \
            .with_reading_index(1) \
            .with_count_index(6) \
            .read()
        bag.extend_overlap(other)
    return bag
