from typing import Optional

from occurrence import OccurrenceBag, OccurrenceReader

def read_bag(path_suw: str, path_luw: Optional[str] = None) -> OccurrenceBag:
    bag = OccurrenceReader() \
        .with_path(path_suw) \
        .with_separator("\t") \
        .with_text_index(2) \
        .with_reading_index(1) \
        .with_count_index(6) \
        .read()
    if path_luw:
        other = OccurrenceReader() \
            .with_path(path_luw) \
            .with_separator("\t") \
            .with_skip_lines(1) \
            .with_text_index(2) \
            .with_reading_index(1) \
            .with_count_index(6) \
            .read()
        bag.extend_overlap(other)
    return bag
