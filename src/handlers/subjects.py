from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.keyboards import get_back_btn, get_back_btn_kb, get_user_subjects_btns
from src.service import UserService
from src.middlewares import error_handler
from src.states import AddSubjectState
from src.texts import subjects_list_is_null, add_subject_instruction, answer_on_format_error
from src.utils import escape_html


router = Router()

@router.callback_query(F.data == 'subjects')
@error_handler
async def subjects(callback: types.CallbackQuery):
    user_service = UserService()
    subjects = await user_service.get_user_subjects(callback.message.chat.id)

    buttons = await get_user_subjects_btns(
        chat_id=callback.message.chat.id,
        item_id_prefix='subject_'
    )
    
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
async def get_subject(callback: types.CallbackQuery):
    user_service = UserService()
    subject_id = int(callback.data.split('_')[-1]) # type: ignore
    subject = await user_service.get_subject(
        chat_id=callback.message.chat.id, 
        subject_id=subject_id
    )

    answer = (
        f'Предмет: {escape_html(subject.title)}\n'
        f'Соотношение часов: {subject.numerator}/{subject.denominator}\n'
    )

    await callback.message.edit_text(answer, reply_markup=get_back_btn_kb(data='subjects'))
    await callback.answer()

@router.callback_query(StateFilter(None), F.data == 'add_subject')
@error_handler
async def add_subject(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(add_subject_instruction, reply_markup=get_back_btn_kb())
    await state.set_state(AddSubjectState.subject_name_and_coef)

@router.message(AddSubjectState.subject_name_and_coef, F.text)
@error_handler
async def add_subject_name_and_coef(message: types.Message, state: FSMContext):
    subjects = []
    try:
        for subject_text in message.text.split('\n'):
            subject_text = subject_text.strip()
            title = subject_text[:-3] # type: ignore
            numerator, denominator = map(int, subject_text[-3:].split('/')) # type: ignore
            subjects.append([title, numerator, denominator])
    except ValueError:
        await message.answer(answer_on_format_error, reply_markup=get_back_btn_kb())
        return

    answer = ''
    user_service = UserService()
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
    user_service = UserService()

    deleted_subject = await user_service.delete_subject(callback.message.chat.id, subject_id)

    msg_title = (
        f'Предмет <b>{escape_html(deleted_subject.title)}</b> упешно удален.\n'
        'Ты можешь удалить что-то еще или вернуться назад:'
    )

    await delete_subject_menu(callback, msg_title=msg_title)
