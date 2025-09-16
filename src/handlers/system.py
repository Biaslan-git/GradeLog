from aiogram import Router, F, types

from src.bot import bot
from src.config import settings

router = Router()

@router.message(F.text.startswith('/report'))
async def process_report(message: types.Message):
    if data := message.text.replace('/report', ''):
        data_split = data.split('x')
        if len(data_split) == 2 and data_split[0].isdigit() and data_split[1].isdigit():
            await bot.forward_message(
                chat_id=settings.OWNER_CHAT_ID,
                from_chat_id=int(data_split[0]),
                message_id=int(data_split[1])
            )
