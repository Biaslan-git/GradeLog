from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service import UserService


main_kb_btns = [
    [InlineKeyboardButton(text='Мои предметы', callback_data='subjects')],
    [InlineKeyboardButton(text='Добавить предмет', callback_data='add_subject')],
    # [InlineKeyboardButton(text='Добавить баллы', callback_data='add_grades')],
    [InlineKeyboardButton(text='Удалить предмет', callback_data='delete_subject')],
]
main_kb = InlineKeyboardMarkup(inline_keyboard=main_kb_btns)


BACK_BUTTON_DATA = 'main_clear_state' 
BACK_BUTTON_TEXT = '⬅ Назад'

def get_back_btn(
    data: str = BACK_BUTTON_DATA, 
    text: str = BACK_BUTTON_TEXT
) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=text,
        callback_data=data
    )]

def get_back_btn_kb(
    data: str = BACK_BUTTON_DATA, 
    text: str = BACK_BUTTON_TEXT
) -> InlineKeyboardMarkup:
    button = get_back_btn(
        data=data, 
        text=text,
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[button])
    return kb

async def get_user_subjects_btns(
    chat_id: int,
    item_id_prefix: str,
    item_title_prefix: str = '',
    item_title_suffix: str = ''
) -> list[list[InlineKeyboardButton]]:
    user_service = UserService()
    subjects = await user_service.get_user_subjects(chat_id)
    
    buttons = []
    for subject in subjects:
        buttons.append([InlineKeyboardButton(
            text=f'{item_title_prefix}{subject.title}{item_title_suffix}',
            callback_data=f'{item_id_prefix}{subject.id}'
        )])

    return buttons

