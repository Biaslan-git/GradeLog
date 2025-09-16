from aiogram import Bot, Dispatcher

from src.config import settings

assert settings.BOT_TOKEN, "missing BOT_TOKEN variable in .env file"
bot = Bot(token=settings.BOT_TOKEN)


