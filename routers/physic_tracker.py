import asyncio

from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from db.db import db_session
from db.models import PhysicalHealth
from utils import send_message

router = Router()

class PhysicalStates(StatesGroup):
    ask_to_enter = State()


@router.message(Command(commands=["enter_sport"]))
async def handle_start(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите сколько калории вы сожгли, когда занимались спортом")
    await state.set_state(PhysicalStates.ask_to_enter)


@router.message(StateFilter(PhysicalStates.ask_to_enter))
async def handle_sport_enter(message: types.Message, state: FSMContext):
    value = message.text
    if not validate_calories(value):
        asyncio.gather(
            send_message(message, "Вы неправильно ввели колории. Это значение должно быть целым неотрицательным числом. Пожалуйста, введите его обратно"),    
            state.set_state(PhysicalStates.ask_to_enter)
        )
        return

    value = int(value)
    user_id = message.from_user.id
    try:
        obj = PhysicalHealth(userId=user_id, calories=value)
        db_session.add(obj)
        db_session.commit()
        asyncio.gather(
            send_message(message, "✅ Спасибо, что ввели данные!\n📊 Не забывайте — вы всегда можете попросить у меня график с вашими данными для удобного отслеживания."),
            state.clear()
        )
    except ...:
        print(ex)
        asyncio.gather(
            send_message(message, "Произошла ошибка при сохранении данных. Пожалуйста, попробуйте заново."),
            state.set_state(PhysicalStates.ask_to_enter)
        )


def validate_calories(value):
    try:
        value = int(value)
        return value >= 0
    except BaseException as ex:
        return False
