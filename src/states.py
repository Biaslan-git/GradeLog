from aiogram.fsm.state import StatesGroup, State

class AddSubjectState(StatesGroup):
    subject_name_and_coef = State()

class AddGradesState(StatesGroup):
    grades = State()
