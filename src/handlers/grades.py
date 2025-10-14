from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.service import UserService
from src.middlewares import error_handler
from src.keyboards import get_back_btn, get_back_btn_kb, get_user_subjects_btns
from src.texts import subjects_list_is_null, answer_on_format_error, add_grades_instruction
from src.states import AddGradesState
from src.utils import escape_html

router = Router()

@router.callback_query(F.data == 'add_grades')
@error_handler
async def add_grades(callback: types.CallbackQuery):
    user_service = UserService()
    subjects = await user_service.get_user_subjects(callback.message.chat.id)

    buttons = await get_user_subjects_btns(
        chat_id=callback.message.chat.id,
        item_id_prefix='add_grades_'
    )

    if subjects:
        answer_text = '📚 Выбери предмет для добавления баллов:'
        buttons.append(get_back_btn())
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(answer_text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(
            subjects_list_is_null, 
            reply_markup=get_back_btn_kb()
        )

@router.callback_query(StateFilter(None), F.data.startswith('add_grades_'))
@error_handler
async def add_grades_to_subject(callback: types.CallbackQuery, state: FSMContext):
    try:
        subject_id = int(callback.data.removeprefix('add_grades_'))
        await state.update_data(subject_id=subject_id)
    except:
        await callback.message.edit_text(answer_on_format_error, reply_markup=get_back_btn_kb(data="add_grades"))
        return

    await callback.message.edit_text(add_grades_instruction, reply_markup=get_back_btn_kb(data="add_grades"))
    await state.set_state(AddGradesState.grades)

@router.message(AddGradesState.grades)
@error_handler
async def add_grades_to_subject_send_grades(message: types.Message, state: FSMContext):
    grades = []
    try:
        for grade_text in message.text.split('\n'):
            grade_text = grade_text.strip()
            grade1, grade2 = map(int, grade_text.split()) # type: ignore
            grades.append([grade1, grade2])
    except ValueError:
        await message.answer(answer_on_format_error, reply_markup=get_back_btn_kb())
        return

    user_service = UserService()
    state_data = await state.get_data()
    subject = await user_service.get_subject(message.chat.id, state_data['subject_id'])
    answer = ''
    for grade_data in grades:
        grade = await user_service.add_grade(
            chat_id=message.chat.id,
            subject_id=subject.id,
            grade1=grade_data[0],
            grade2=grade_data[1]
        )
        answer += f'- {grade.grade1} {grade.grade2}\n'

    if grades:
        answer = f'Предмет: <b>{escape_html(subject.title)}</b>\nДобавленные баллы:\n' + answer
    else:
        await message.answer(answer_on_format_error, reply_markup=get_back_btn_kb(data='add_grades'))
        return

    kb_btns = [
        [types.InlineKeyboardButton(text=subject.title, callback_data=f'subject_{subject.id}')],
        get_back_btn(data='add_grades')
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=kb_btns)

    await message.answer(answer, reply_markup=kb)
    await state.clear()
