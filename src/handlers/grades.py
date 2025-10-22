from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.handlers.subjects import get_subject
from src.service import user_service
from src.middlewares import error_handler
from src.keyboards import get_back_btn, get_back_btn_kb
from src.texts import answer_on_format_error, add_grades_instruction
from src.states import AddGradesState
from src.utils import escape_html

router = Router()


@router.callback_query(F.data.startswith('grades:'))
@error_handler
async def subject_grades(callback: types.CallbackQuery):
    subject_id = int(callback.data.removeprefix('grades:'))

    subject = await user_service.get_subject(callback.message.chat.id, subject_id)
    grades = await user_service.get_subject_grades(
        callback.message.chat.id,
        subject_id
    )

    answer = (
        f'<b>Предмет:</b> <i>{escape_html(subject.title)}</i>\n\n'
    )

    btns = []
    if grades:
        answer += 'Баллы:\n'
        row = []
        for idx, grade in enumerate(grades, start=1):
            answer += f'{idx}. {grade.grade1} {grade.grade2}\n'

            row.append(types.InlineKeyboardButton(text=f'{idx}', callback_data=f'grade:{grade.id}'))

            if len(row) % 3 == 0:
                btns.append(row)
                row = []

        if row:
            btns.append(row)

    else:
        answer += 'Нет добавленных баллов.'

    btns.append(get_back_btn(data=f'subject_{subject_id}'))
    kb = types.InlineKeyboardMarkup(inline_keyboard=btns, row_width=3)
    await callback.message.edit_text(answer, reply_markup=kb)


@router.callback_query(F.data.startswith('grade:'))
@error_handler
async def grade_detail(callback: types.CallbackQuery):
    grade_id = int(callback.data.removeprefix('grade:'))
    try:
        grade = await user_service.get_grade(grade_id)
    except ValueError:
        await callback.answer('Такого предмета не существует!')
        return

    answer = (
        f'<b>Предмет:</b> <i>{escape_html(grade.subject.title)}</i>'
        f'<b>Выбранная пара баллов:</b> <i>{grade.grade1} {grade.grade2}</i>'
    )
    
    btns = [
        [types.InlineKeyboardButton(text=f'❌ Удалить', callback_data=f'delete_grade:{grade.id}')],
        get_back_btn(data=f'subject_{grade.subject.id}')
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=btns)

    await callback.message.edit_text(answer, reply_markup=kb)

@router.callback_query(F.data.startswith('delete_grade:'))
@error_handler
async def delete_grade(callback: types.CallbackQuery):
    grade_id = int(callback.data.removeprefix('delete_grade:'))
    try:
        grade = await user_service.delete_grade(callback.message.chat.id, grade_id)
    except ValueError:
        await callback.answer('Такого предмета не существует!')
        return
    
    await callback.message.edit_text(
        f'✅ Баллы успешно удалены!', 
        reply_markup=get_back_btn_kb(data=f'grades:{grade.subject.id}')
    )

@router.callback_query(StateFilter(None), F.data.startswith('add_grades_'))
@error_handler
async def add_grades_enter_grades(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.removeprefix('add_grades_'))
    await state.update_data(subject_id=subject_id)

    subject = await user_service.get_subject(callback.message.chat.id, subject_id)

    await callback.message.edit_text(
        f'<b>Предмет:</b> <i>{escape_html(subject.title)}</i>\n\n'+add_grades_instruction, 
        reply_markup=get_back_btn_kb(data=f"add_grades_back_to_subject:{subject_id}"))
    await state.set_state(AddGradesState.grades)

@router.message(AddGradesState.grades)
@error_handler
async def add_grades_to_subject_send_grades(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    subject_id = state_data['subject_id']
    grades = []
    try:
        for row in message.text.split('\n'):
            row = row.strip()
            row_splt = row.split()
            grade1, grade2 = map(int, row_splt) if len(row_splt) == 2 else row # type: ignore
            grades.append([grade1, grade2])
    except ValueError:
        await message.answer(
            answer_on_format_error, 
            reply_markup=get_back_btn_kb(data=f"add_grades_back_to_subject:{subject_id}")
        )
        return

    subject = await user_service.get_subject(message.chat.id, subject_id)
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
        await message.answer(
            answer_on_format_error, 
            reply_markup=get_back_btn_kb(data=f"add_grades_back_to_subject:{subject_id}")
        )
        return

    kb_btns = [
        [types.InlineKeyboardButton(text=subject.title, callback_data=f'subject_{subject.id}')],
        get_back_btn(data='subjects', text='Мои предметы')
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=kb_btns)

    await message.answer(answer, reply_markup=kb)
    await state.clear()

@router.callback_query(AddGradesState.grades, F.data.startswith('add_grades_back_to_subject'))
@error_handler
async def add_grades_enter_grade_back_btn(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    subject_id = int(callback.data.removeprefix('add_grades_back_to_subject:'))
    await get_subject(callback, subject_id)
