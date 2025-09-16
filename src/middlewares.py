from functools import wraps
import traceback

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def error_handler(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        try:
            await func(message, *args, **kwargs)  # Без return
        except Exception as e:
            error_message = traceback.format_exc(limit=1)

            error_message = f'Произошла ошибка:\n{message.chat.id}\n{func.__name__}: {error_message}'

            msg = await message.answer(f'{error_message}')
            await message.answer(f'Нажми /report{msg.chat.id}x{msg.message_id}, чтобы сообщить об этом разработчику')
    return wrapper


