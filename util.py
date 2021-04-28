from typing import Iterable


def flatten(seq: Iterable[Iterable]) -> list:
    return sum((list(sub_seq) for sub_seq in seq), start=[])
