from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


main_kb_btns = [
    [InlineKeyboardButton(text='Мои предметы', callback_data='subjects')],
    [InlineKeyboardButton(text='Добавить предмет', callback_data='add_subject')],
    # [InlineKeyboardButton(text='Добавить баллы', callback_data='add_subject')],
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
