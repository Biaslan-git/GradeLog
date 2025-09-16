from aiogram import Router, F, types
from aiogram.filters import Command

from sqlalchemy.exc import IntegrityError

from src.service import UserService, add_user
from src.middlewares import error_handler

router = Router()

@router.message(Command("start"))
@error_handler
async def cmd_start(message: types.Message):
    start_message = (
        f"Привет, {message.from_user.full_name}, я бот для учета и анализа учебных оценок!\n"
        'Вот, что я умею:\n'
        '/subjects - вывести список предметов'
    )
    await message.answer(start_message)

    try:
        user_service = UserService()
        await user_service.add_user(message.chat.id, message.from_user.username, message.from_user.full_name)
    except ValueError:
        pass

@router.message(Command('subjects'))
@error_handler
async def subjects(message: types.Message):
    pass

