from aiogram import Router, F, types

from src.bot import bot
from src.config import settings
from src.handlers.main import main_menu

router = Router()

@router.callback_query(F.data == 'report')
async def process_report(callback: types.CallbackQuery):
    await bot.send_message(
        chat_id=settings.OWNER_CHAT_ID,
        text=callback.message.text,
        parse_mode=None
    )

    await main_menu(callback)

@router.callback_query(F.data == 'mute')
async def mute(callback: types.CallbackQuery):
    await callback.answer("Эта кнопка не кликабельна!")
