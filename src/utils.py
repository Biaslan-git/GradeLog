from typing import Sequence
from src.models import Grade, Subject, SubjectType
from src.constants import grades_to_marks_table
from src.schemas import SubjectStatSchema


def escape_html(text: str) -> str:
    """Экранирует специальные HTML-символы в строке."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))


def get_subject_stat(subject: Subject, subject_grades: Sequence[Grade]) -> SubjectStatSchema:
    """
    Возвращает статистику по предмету на основе оценок и таблицы порогов.
    """
    cur_grade_sum = sum(g.grade1 + g.grade2 for g in subject_grades)
    cur_classes_count = len(subject_grades)
    max_points = cur_classes_count * 2

    key = f"{subject.numerator}/{subject.denominator}"
    mark_table = grades_to_marks_table.get(key, {})

    def calc_threshold(name: str):
        val = mark_table.get(name)
        return int(max_points * val) if val is not None else None

    need_for_ok = calc_threshold("ok")
    need_for_passed = calc_threshold("passed")
    need_for_good = calc_threshold("good")
    need_for_great = calc_threshold("great")

    if subject.subject_type == SubjectType.EXAM:
        if need_for_great and cur_grade_sum >= need_for_great:
            cur_mark, cur_mark_icon = "отлично", "✅"
        elif need_for_good and cur_grade_sum >= need_for_good:
            cur_mark, cur_mark_icon = "хорошо", "✅"
        elif need_for_ok and cur_grade_sum >= need_for_ok:
            cur_mark, cur_mark_icon = "удовлетворительно", "⭕"
        else:
            cur_mark, cur_mark_icon = "слишком мало баллов", "❌"
    else:
        if need_for_passed and cur_grade_sum >= need_for_passed:
            cur_mark, cur_mark_icon = "зачтено", "✅"
        else:
            cur_mark, cur_mark_icon = "слишком мало баллов", "❌"


    return SubjectStatSchema(
        cur_classes_count=cur_classes_count,
        cur_grades_sum=cur_grade_sum,
        cur_mark=cur_mark,
        cur_mark_icon=cur_mark_icon,
        cur_mark_with_icon=f"{cur_mark_icon} {cur_mark}",
        need_for_ok=need_for_ok,
        need_for_passed=need_for_passed,
        need_for_good=need_for_good,
        need_for_great=need_for_great,
    )


def get_subject_icon(subject: Subject, subject_grades: Sequence[Grade]) -> str:
    """
    Возвращает только иконку текущего статуса по сумме баллов.
    """
    cur_grade_sum = sum(g.grade1 + g.grade2 for g in subject_grades)
    cur_classes_count = len(subject_grades)
    max_points = cur_classes_count * 2

    key = f"{subject.numerator}/{subject.denominator}"
    mark_table = grades_to_marks_table.get(key, {})

    def calc_threshold(name: str):
        val = mark_table.get(name)
        return int(max_points * val) if val is not None else None

    need_for_ok = calc_threshold("ok")
    need_for_passed = calc_threshold("passed")
    need_for_good = calc_threshold("good")
    need_for_great = calc_threshold("great")

    if subject.subject_type == SubjectType.EXAM:
        if need_for_great and cur_grade_sum >= need_for_great:
            return "✅"
        elif need_for_good and cur_grade_sum >= need_for_good:
            return "✅"
        elif need_for_ok and cur_grade_sum >= need_for_ok:
            return "⭕"
        else:
            return "❌"
    else:
        if need_for_passed and cur_grade_sum >= need_for_passed:
            return "✅"
        else:
            return "❌"

