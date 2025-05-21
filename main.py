import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from routers.glucose_tracker import router as glucose_router
from routers.physic_tracker import router as physical_router
from routers.welcome import router as welcome_router

from keys import BOT_API_KEY

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="enter_glucose", description="Ввести уровень глюкозы"),
        BotCommand(command="enter_sport", description="Ввести данные о физ активности"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_API_KEY)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(welcome_router, glucose_router, physical_router)
    await set_bot_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
