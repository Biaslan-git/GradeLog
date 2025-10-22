from dataclasses import dataclass
from typing import NamedTuple


class TraditionalSystemMarks(NamedTuple):
    passed = ''
    ok = 'ok'
    good = 'good'
    great = 'great'

@dataclass
class SubjectStatSchema:
    cur_classes_count: int
    cur_grades_sum: int
    cur_mark: str
    cur_mark_icon: str
    cur_mark_with_icon: str
    need_for_ok: int | None
    need_for_passed: int | None
    need_for_good: int | None
    need_for_great: int | None


