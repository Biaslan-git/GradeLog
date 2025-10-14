from aiogram import Router, types, F
from aiogram.filters import Command 

from src.service import UserService
from src.middlewares import error_handler
from src.texts import start_message
from src.keyboards import main_kb

router = Router()

@router.message(Command("start"))
@error_handler
async def cmd_start(message: types.Message):
    await message.answer(
        start_message,
        reply_markup=main_kb
    )

    try:
        user_service = UserService()
        await user_service.add_user(message.chat.id, message.from_user.username, message.from_user.full_name)
    except ValueError:
        pass

@router.callback_query(F.data.startswith('main'))
@error_handler
async def main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text( # type: ignore
        'Главное меню:',
        reply_markup=main_kb
    )





