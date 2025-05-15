import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from dotenv import load_dotenv
import pytz
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from aiogram.fsm.storage.base import StorageKey

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db import Supabase, UserManager, FeedbackManager
from utils import convert_to_image, get_week_start
from ai import AIClient

logging.basicConfig(
    level=logging.INFO,  # Use DEBUG for more detailed output
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
logging.getLogger("aiogram").setLevel(logging.INFO)

load_dotenv()
API_TOKEN = os.getenv("BOT_API_KEY")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

supabase = Supabase()
user_manager = UserManager(supabase.db)
feedback_manager = FeedbackManager(supabase.db)

ai_client = AIClient(GOOGLE_AI_API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Dialog(StatesGroup):
    asking_diet = State()
    asking_physical_health = State()
    asking_mental_health = State()


async def send_message(text: str, message: Message, parse_mode=None):
    if parse_mode:
        await message.answer(text, parse_mode=parse_mode)
    else:
        await message.answer(text)


async def send_long_message(chat_id, text, parse_mode="HTML"):
    max_length = 4096
    for i in range(0, len(text), max_length):
        if parse_mode:
            await bot.send_message(
                chat_id, text[i : i + max_length], parse_mode=parse_mode
            )
        else:
            await bot.send_message(chat_id, text[i : i + max_length])


async def get_daily_ai_feedback(data: dict) -> str:
    payload = []
    if "images" in data["diet"]:
        payload += data["diet"]["images"]

    message = (
        "Представь что я болею сахарным диабетом. \n\n"
        "На основе этой информации \n"
        f"Питание (все фотографии, которые я прикрепил относятся к питанию): {data["diet"]["content"]}\n"
        f"Физическая активность: {data["physical_health"]}\n"
        f"Ментальное состояние: {data["mental_health"]}\n\n\n"
        "Представь, что ты мой доктор и сформулируй краткий и точный ответ. "
        "Дай полезные рекомендации по питанию, активности и ментальному здоровью. "
        "Ответ должен быть максимум 10 предложения, понятным и информативным."
        "Используй только тег <b></b> (для жирного текста, но никак не ** / *) и простой текст!!. Никаких других тегов!! Добавление смайликов приветствуется.\n"
        "Не пиши привет или здравствуйте и не здоровайся со мной. Просто дай советы. Раздели секции новой строкой."
    )

    payload.append(message)
    ai_response = ai_client.generate(*payload)
    if ai_response.startswith("```html"):
        ai_response = ai_response[7:]
    while ai_response.endswith("```"):
        ai_response = ai_response[: len(ai_response) - 3]
    return ai_response


async def get_weekly_ai_feedback(user_id: int) -> str:
    start_date = get_week_start()

    data = feedback_manager.get(user_id, start_date=start_date)
    message = (
        "Представь что я болею сахарным диабетом. И на протяжении недели меня консультировал ты. \n\n"
        "Вот его советы и обратная связь по этой неделе \n"
        f"{"\n\n\n".join([d["content"] for d in data])}\n\n\n"
        "Дай подробный отчет, помоги оценить прогресс и дай полезные советы. "
        "Дай полезные рекомендации по питанию, активности и ментальному здоровью. "
        "Ответ должен быть максимум 20 предложения, понятным и информативным."
        "Используй только тег <b></b> (для жирного текста, но никак не ** / *) и простой текст!!. Никаких других тегов!! Добавление смайликов приветствуется.\n"
        "Не пиши привет или здравствуйте и не здоровайся со мной. Просто дай советы. Раздели секции новой строкой."
    )
    ai_response = ai_client.generate(message)
    if ai_response.startswith("```html"):
        ai_response = ai_response[7:]
    while ai_response.endswith("```"):
        ai_response = ai_response[: len(ai_response) - 3]
    return ai_response


async def save_feedback_to_db(feedback: str, user_id):
    data = {"user_id": user_id, "content": feedback}
    feedback_manager.create(**data)


async def send_weekly_feedback(user_id: int, chat_id: int):
    ai_response = await get_weekly_ai_feedback(user_id)
    await send_long_message(chat_id, ai_response)


async def start_daily_feedback(user_id: int, chat_id: int):
    await bot.send_message(
        chat_id,
        "Привет! 🍽️ Как прошло твое питание сегодня? Можешь прикрепить фотографии если хочешь",
    )
    state = FSMContext(
        storage=dp.storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=chat_id,
            user_id=user_id,
        ),
    )
    await state.set_state(Dialog.asking_diet)


@dp.message(Command(commands=["start"]))
async def start_handler(message: Message, state: FSMContext):
    tel_id = message.from_user.id
    user_exists = any([d["id"] == tel_id for d in user_manager.get_all()])
    available_commands = [
        "start",
        "start_daily_feedback",
        "start_weekly_feedback",
    ]
    if user_exists:
        await message.answer(
            f"Вы уже зарегистрированы в нашей системе.\nНиже можете увидеть доступные команды: \n{''.join([("/" + cmd + "\n") for cmd in available_commands])}"
        )
        return

    user_manager.create(
        **{
            "id": message.from_user.id,
            "chat_id": message.chat.id,
        }
    )
    welcome_text = (
        "👋 **Привет!**\n"
        "Добро пожаловать в **[DiaDoc]** – ваш личный помощник в поддержании здоровья при сахарном диабете! 💙\n\n"
        "✨ **Как я помогу вам?**\n"
        "🕗 **Каждый день в 8 вечера** я буду спрашивать вас о:\n"
        "🍽️ Питании\n"
        "🏃 Физической активности\n"
        "😊 Вашем настроении\n\n"
        "📊 **Раз в неделю** я подготовлю для вас подробный отчет, помогу оценить прогресс и дам полезные советы!\n\n"
        "💬 В любое время вы можете задать мне вопросы – я всегда на связи!\n\n"
        "Моя цель – сделать заботу о вашем здоровье удобной и поддерживающей. Давайте двигаться к лучшему самочувствию вместе! 🚀"
        f"Ниже можете увидеть доступные команды: \n{''.join([("/" + cmd + "\n") for cmd in available_commands])}"
    )
    await message.answer(welcome_text, parse_mode="Markdown")
    await state.clear()


@dp.message(Command(commands=["start_weekly_feedback"]))
async def start_weekly_feedback_handler(message: Message, state: FSMContext):
    await asyncio.gather(
        send_weekly_feedback(message.from_user.id, message.chat.id), state.clear()
    )


@dp.message(Command(commands=["start_daily_feedback"]))
async def start_daily_feedback_handler(message: Message, state: FSMContext):
    await message.answer(
        "Привет! 🍽️ Как прошло твое питание сегодня? Можешь прикрепить фотографии если хочешь"
    )
    await state.set_state(Dialog.asking_diet)


@dp.message(StateFilter(Dialog.asking_diet))
async def diet_handler(message: Message, state: FSMContext):
    data = {
        "diet": {
            "content": message.text,
        }
    }
    if message.photo:
        data["diet"]["images"] = [
            await convert_to_image(photo, bot) for photo in message.photo
        ]
        data["diet"]["content"] = message.caption

    await message.answer("🏃 Какие физические упражнения ты делал(а) сегодня?")
    await state.update_data(data)
    await state.set_state(Dialog.asking_physical_health)


@dp.message(StateFilter(Dialog.asking_physical_health))
async def physical_health_handler(message: Message, state: FSMContext):
    await state.update_data({"physical_health": message.text})
    await message.answer("😊 Как ты себя чувствовуешь? Был ли стресс?")
    await state.set_state(Dialog.asking_mental_health)


@dp.message(StateFilter(Dialog.asking_mental_health))
async def mental_health_handler(message: Message, state: FSMContext):
    await state.update_data({"mental_health": message.text})
    user_data = await state.get_data()
    ai_feedback = (await get_daily_ai_feedback(user_data)).strip()

    await asyncio.gather(
        send_long_message(message.chat.id, ai_feedback),
        save_feedback_to_db(ai_feedback, message.from_user.id),
        state.clear(),
    )


@dp.message(F.text)
async def text_handler(message: Message, state: FSMContext):
    await state.clear()

    prompt = (
        "Ответь на следующий вопрос:\n\n\n"
        f"{message.text}\n\n\n"
        "Ответ должен быть максимум 10 предложения, понятным и информативным."
        "Используй только тег <b></b> (для жирного текста, но никак не ** / *) и простой текст!!. Никаких других тегов!! Добавление смайликов приветствуется.\n"
        "Не пиши привет или здравствуйте и не здоровайся со мной. Просто дай ответ."
    )
    ai_response = ai_client.generate(prompt)
    await send_long_message(message.chat.id, ai_response)


async def setup_scheduler():
    async def send_weekly_feedback_coroutine():
        users = user_manager.get_all()
        await asyncio.gather(
            *[send_weekly_feedback(user["id"], user["chat_id"]) for user in users]
        )

    async def send_daily_feedback_coroutine():
        users = user_manager.get_all()
        await asyncio.gather(
            *[start_daily_feedback(user["id"], user["chat_id"]) for user in users]
        )

    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Almaty"))
    scheduler.add_job(
        send_weekly_feedback_coroutine,
        CronTrigger(day_of_week="sun", hour=21, minute=0),
    )
    scheduler.add_job(send_daily_feedback_coroutine, CronTrigger(hour=20, minute=0))
    scheduler.start()


@dp.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await setup_scheduler()


async def main():
    logger.log(logging.INFO, "Your slave is ready to work!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
