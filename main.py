import asyncio
import logging

from aiogram import Dispatcher

from src.handlers import routers
from src.bot import bot

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_routers(*routers)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

