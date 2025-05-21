from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["start"]))
async def handle_welcome(message: types.Message):
    await message.answer(
        ("👋 Привет! Добро пожаловать на платформу **DiaDoc**!\n\n"
        "Я твой помощник, который поможет следить за твоим уровнем сахара в крови 🍬, питанием 🥗, физическим 🏃 и ментальным 🧠 здоровьем.\n\n"
        "Каждый день я буду напоминать тебе внести данные, чтобы ты ничего не забыл 📅.\n"
        "Позже ты сможешь легко экспортировать всё в виде наглядных графиков 📊 — это удобно как для тебя, так и для консультации с врачом 👨‍⚕️👩‍⚕️.\n\n"
        "Готов начать? 😊\n"
        "📋 На панели ты всегда найдёшь список доступных команд. Просто выбери нужную, когда понадобится! 😉"),
        parse_mode="Markdown"
    )
