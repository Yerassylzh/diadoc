import asyncio

from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from db.db import db_session
from db.models import Glucose
from utils import send_message

router = Router()

class GlucoseStates(StatesGroup):
    ask_to_enter = State()


@router.message(Command(commands=["enter_glucose"]))
async def handle_start(message: types.Message, state: FSMContext):
    await message.answer("🩸 Пожалуйста, введите уровень глюкозы на сегодня (ммоль/л). Очень важно указать точное значение для точного отслеживания здоровья!")
    await state.set_state(GlucoseStates.ask_to_enter)


@router.message(StateFilter(GlucoseStates.ask_to_enter))
async def handle_glucose_enter(message: types.Message, state: FSMContext):
    glucose = message.text
    if not validate_glucose(glucose):
        await asyncio.gather(
            send_message(message, "Вы неправильно ввели уровень глюкозы (ммоль/л). Это значение должно быть числом. Пожалуйста, введите его обратно"),
            state.set_state(GlucoseStates.ask_to_enter)
        )
        return

    user_id = message.from_user.id
    try:
        obj = Glucose(userId=user_id, value=glucose)
        db_session.add(obj)
        db_session.commit()
        asyncio.gather(
            send_message(message, "✅ Спасибо, что ввели уровень сахара!\n📊 Не забывайте — вы всегда можете попросить у меня график с вашими данными для удобного отслеживания."),
            state.clear()
        )
    except BaseException as ex:
        print(ex)
        asyncio.gather(
            send_message(message, "Произошла ошибка при сохранении данных. Пожалуйста, попробуйте заново."),
            state.set_state(GlucoseStates.ask_to_enter)
        )


def validate_glucose(value):
    try:
        value = float(value)
        return value >= 0
    except BaseException as ex:
        return False
