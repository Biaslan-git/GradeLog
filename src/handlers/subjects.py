from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.models import SubjectType
from src.keyboards import get_back_btn, get_back_btn_kb, get_user_subjects_btns
from src.service import user_service
from src.middlewares import error_handler
from src.states import AddSubjectState
from src.texts import subjects_list_is_null, add_subject_instruction, answer_on_format_error
from src.utils import escape_html, get_subject_icon, get_subject_stat

import re


router = Router()

@router.callback_query(F.data == 'subjects')
@error_handler
async def subjects(callback: types.CallbackQuery):
    subjects = await user_service.get_user_subjects(callback.message.chat.id)

    buttons = []
    for subject in subjects:
        subject_grades = subject.grades
        mark_icon = get_subject_icon(subject, subject_grades)
        buttons.append([types.InlineKeyboardButton(
            text=f'{subject.title} {mark_icon}',
            callback_data=f'subject_{subject.id}'
        )])
    
    if subjects:
        answer_text = '📚 Твои предметы:'
        buttons.append(get_back_btn())
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(answer_text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(
            subjects_list_is_null, 
            reply_markup=get_back_btn_kb()
        )

@router.callback_query(F.data.startswith('subject_'))
@error_handler
async def get_subject(callback: types.CallbackQuery, subject_id: int | None = None):
    subject_id = int(callback.data.split('_')[-1]) if subject_id is None else subject_id
    subject = await user_service.get_subject(
        chat_id=callback.message.chat.id, 
        subject_id=subject_id
    )
    grades = await user_service.get_subject_grades(
        chat_id=callback.message.chat.id, #type: ignore
        subject_id=subject.id
    )

    subject_stat = get_subject_stat(subject, grades)

    if subject.subject_type == SubjectType.EXAM:
        stat_text = '<b>Шкала оценивания</b>\n'
        stat_text += (
            f'<b>Удовлетворительно</b>: <i>{f'⭕ {subject_stat.need_for_ok}' or '-'}</i>\n'
            f'<b>Хорошо</b>: <i>{f'✅ {subject_stat.need_for_good}' or '-'}</i>\n'
            f'<b>Отлично</b>: <i>{f'✅ {subject_stat.need_for_great}' or '-'}</i>\n'
        ) if subject_stat.cur_grades_sum else 'Не хватает данных'
    else:
        stat_text = (
            '<b>Шкала оценивания</b>\n'
        )
        stat_text += f'<b>Зачтено</b>: <i>{f'✅ {subject_stat.need_for_passed}' or '-'}</i>\n' if subject_stat.cur_grades_sum else 'Не хватает данных'

    
    answer = (
        f'<b>Предмет:</b> <i>{escape_html(subject.title)}</i>\n'
        f'<b>Соотношение часов:</b> <i>{subject.numerator}/{subject.denominator}</i>\n'
        f'<b>Текущее кол-во пар:</b> <i>{subject_stat.cur_classes_count}</i>\n'
        f'<b>Текущее кол-во баллов:</b> <i>{subject_stat.cur_grades_sum}</i>\n'
        f'<b>Текущая отметка:</b> <i>{subject_stat.cur_mark_with_icon if subject_stat.cur_grades_sum else 'Не хватает данных' }</i>\n\n'
        f'{stat_text}'
    )

    btns = [
        [types.InlineKeyboardButton(text=f'Тип: {subject.subject_type.value}', callback_data=f'switch_subject_type:{subject.id}')],
        [types.InlineKeyboardButton(text='Показать баллы', callback_data=f'grades:{subject.id}')],
        [types.InlineKeyboardButton(text='Добавить баллы', callback_data=f'add_grades_{subject.id}')]
    ]

    btns.append(get_back_btn(data='subjects'))
    kb = types.InlineKeyboardMarkup(inline_keyboard=btns)

    await callback.message.edit_text(answer, reply_markup=kb)

@router.callback_query(F.data.startswith('switch_subject_type:'))
@error_handler
async def change_subject_type(callback: types.CallbackQuery):
    subject_id = int(str(callback.data).split(':')[1])
    subject = await user_service.get_subject(callback.message.chat.id, subject_id)
    new_subject = await user_service.change_subject_type(callback.message.chat.id, subject_id, subject.subject_type.next())

    await get_subject(callback, new_subject.id)




@router.callback_query(StateFilter(None), F.data == 'add_subject')
@error_handler
async def add_subject(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(add_subject_instruction, reply_markup=get_back_btn_kb())
    await state.set_state(AddSubjectState.subject_name_and_coef)

@router.message(AddSubjectState.subject_name_and_coef, F.text)
@error_handler
async def add_subject_name_and_coef(message: types.Message, state: FSMContext):
    subjects = []
    forbidden_symbols_pattern = re.compile(r'[<>("&\']')  # Запрещенные символы без '/'

    try:
        for subject_text in message.text.split('\n'):
            subject_text = subject_text.strip()
            if forbidden_symbols_pattern.search(subject_text):  # Проверка на запрещенные символы
                await message.answer("Имя предмета содержит запрещенные символы!", reply_markup=get_back_btn_kb())
                return

            title = subject_text[:-3]  # type: ignore
            numerator, denominator = map(int, subject_text[-3:].split('/'))  # type: ignore
            subjects.append([title, numerator, denominator])
    except ValueError:
        await message.answer(answer_on_format_error, reply_markup=get_back_btn_kb())
        return

    answer = ''
    for subject_data in subjects:
        subject = await user_service.add_subject(
            chat_id=message.chat.id,
            title=subject_data[0],
            numerator=subject_data[1],
            denominator=subject_data[2]
        )
        answer += f'- {escape_html(subject.title)} ({subject.numerator}/{subject.denominator})\n'

    if len(subjects) > 1:
        answer = 'Предметы добавлены:\n' + answer
    elif len(subjects) == 1:
        answer = 'Предмет добавлен:\n' + answer
    else:
        await message.answer(answer_on_format_error, reply_markup=get_back_btn_kb())
        return

    await message.answer(answer, reply_markup=get_back_btn_kb())
    await state.clear()

@router.callback_query(F.data.startswith('page_subject_'))
@error_handler
async def get_subject_with_page(callback: types.CallbackQuery):
    page = int(callback.data.split('_')[-1])
    return await get_subject(callback, page)


@router.callback_query(F.data == 'delete_subject')
@error_handler
async def delete_subject_menu(callback: types.CallbackQuery, msg_title: str = 'Выбери предмет для удаления:'):
    buttons = await get_user_subjects_btns(
        chat_id=callback.message.chat.id,
        item_id_prefix='delete_subject_',
        item_title_prefix='✗ ',
        item_title_suffix=' ✗'
    )
    buttons.append(get_back_btn())

    await callback.message.edit_text(
        msg_title, 
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith('delete_subject_'))
@error_handler
async def delete_subject(callback: types.CallbackQuery):
    subject_id = int(callback.data.split('_')[-1])

    deleted_subject = await user_service.delete_subject(callback.message.chat.id, subject_id)

    msg_title = (
        f'Предмет <b>{escape_html(deleted_subject.title)}</b> упешно удален.\n'
        'Ты можешь удалить что-то еще или вернуться назад:'
    )

    await delete_subject_menu(callback, msg_title=msg_title)
