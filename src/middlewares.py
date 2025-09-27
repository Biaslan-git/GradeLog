from functools import wraps
import traceback

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def error_handler(func):
    @wraps(func)
    async def wrapper(message_or_callback: types.Message | types.CallbackQuery, *args, **kwargs):
        try:
            await func(message_or_callback, *args, **kwargs)  # Без return
        except Exception as e:
            message = message_or_callback if type(message_or_callback) == types.Message else message_or_callback.message
            error_message = traceback.format_exc(limit=2)

            error_message = f'Произошла ошибка:\n{message.chat.id}\n{func.__name__}: {error_message}'

            msg = await message.answer(f'{error_message}')
            await message.answer(f'Нажми /report{msg.chat.id}x{msg.message_id}, чтобы сообщить об этом разработчику')
    return wrapper


