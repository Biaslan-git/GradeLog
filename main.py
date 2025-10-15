import asyncio
import logging

from aiogram.types import BotCommand

from src.handlers import routers
from src.bot import bot
from src.dp import dp

logging.basicConfig(level=logging.INFO)


async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

@dp.startup()
async def on_startup(bot):
    await set_commands(bot)
    print("Команды установлены!")



# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_routers(*routers)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

