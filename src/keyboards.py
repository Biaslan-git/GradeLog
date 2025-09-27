from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


main_kb_btns = [
    [InlineKeyboardButton(text='Мои предметы', callback_data='subjects')],
    [InlineKeyboardButton(text='Добавить предмет', callback_data='add_subject')],
    # [InlineKeyboardButton(text='Добавить баллы', callback_data='add_subject')],
]
main_kb = InlineKeyboardMarkup(inline_keyboard=main_kb_btns)


def get_back_btn(
    back_button_data: str = 'main', 
    back_button_text: str = '⬅ Назад'
) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=back_button_text,
        callback_data=back_button_data
    )]

def get_back_btn_kb(
    back_button_data: str = 'main', 
    back_button_text: str = '⬅ Назад'
) -> InlineKeyboardMarkup:
    button = get_back_btn(
        back_button_data='main', 
        back_button_text='⬅ Назад'
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[button])
    return kb
