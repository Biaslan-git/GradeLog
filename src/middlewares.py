from functools import wraps
import traceback

from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.bot import bot
from src.utils import escape_html

def error_handler(func):
    @wraps(func)
    async def wrapper(message_or_callback: types.Message | types.CallbackQuery, *args, **kwargs):
        try:
            await func(message_or_callback, *args, **kwargs)  # Без return
        except Exception as e:
            message = message_or_callback if type(message_or_callback) == types.Message else message_or_callback.message
            error_message = traceback.format_exc(limit=2)

            error_message = f'Произошла ошибка:\n{message.chat.id}\n{func.__name__}: {error_message}'

            await message.answer(
                f'{escape_html(error_message)}',
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                        types.InlineKeyboardButton(
                            text='⬅ Сообщить разработчику и вернуться назад',
                            callback_data=f'report'
                        )
                    ]]
                )
            )
    return wrapper


class ClearStateOnBackMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.CallbackQuery, data: dict):
        state: FSMContext = data.get("state")
        if isinstance(event, types.CallbackQuery) and event.data.endswith('clear_state'):
            await state.clear()
        return await handler(event, data)

class DeleteOldMessageOnCallbackMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.CallbackQuery, data: dict):
        if event.message:  # бывает, что message = None (например, кнопка под инлайн-результатом)
            try:
                await event.message.delete()
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
        
        return await handler(event, data)
