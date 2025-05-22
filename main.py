import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from routers.glucose_tracker import router as glucose_router
from routers.physic_tracker import router as physical_router
from routers.welcome import router as welcome_router
from routers.mental_tracker import router as mental_router
from routers.diet_tracker import router as diet_router
from routers.stats_logger import router as stats_logger_router
from routers.stats_exporter import router as exporter_router

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
        BotCommand(command="enter_mental_health", description="Поделится самочувствием"),
        BotCommand(command="enter_diet", description="Ввести данные о питании"),
        BotCommand(command="log_stats", description="Вывести статистику в чат"),
        BotCommand(command="export_all", description="Экспортировать все данные ввиде pdf файла")
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_API_KEY)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        welcome_router,
        glucose_router,
        physical_router,
        mental_router,
        diet_router,
        stats_logger_router,
        exporter_router
    )
    await set_bot_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
