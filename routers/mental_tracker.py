import asyncio

from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.db import db_session
from db.models import MentalHealth
from utils.base import send_message

router = Router()

class MentalStates(StatesGroup):
    ask_to_enter = State()


class MentalWellnessCallback(CallbackData, prefix="mental_wellness_level"):
    value: int


def create_inlinekeyboard(*buttons: list[tuple[str, any]]):
    builder = InlineKeyboardBuilder()
    for text, data in buttons:
        builder.button(text=text, callback_data=data)
    return builder.adjust(1).as_markup()


@router.message(Command(commands=["enter_mental_health"]))
async def handle_start(message: types.Message, state: FSMContext):
    keyboard = create_inlinekeyboard(
        ("5. 😊 Спокойно", MentalWellnessCallback(value=5)),
        ("4. 🙂 Небольшое напряжение", MentalWellnessCallback(value=4)),
        ("3. 😐 Средний стресс", MentalWellnessCallback(value=3)),
        ("2. 😣 Сильный стресс", MentalWellnessCallback(value=2)),
        ("1. 😫 Крайний стресс", MentalWellnessCallback(value=1))
    )

    await message.answer(
        "Оцените, насколько хорошо вы чувствовали себя сегодня? (5 баллов)",
        reply_markup=keyboard
    )
    await state.set_state(MentalStates.ask_to_enter)


@router.callback_query(MentalWellnessCallback.filter())
async def handle_sport_enter(
    callback: CallbackQuery,
    callback_data: MentalWellnessCallback,
    state: FSMContext
):
    value = callback_data.value
    await state.update_data({"rating": value})
    await callback.message.answer(
        "📝 Добавьте описание:\n"
        "Поделитесь своими мыслями и чувствами за день. Что вас порадовало, что вызвало стресс? 💭🙂😔"
        "Это поможет лучше понять своё состояние и настроение 💡💚"
    )
    await state.set_state(MentalStates.ask_to_enter)


@router.message(StateFilter(MentalStates.ask_to_enter))
async def handle_enter_note(
    message: types.Message,
    state: FSMContext
):
    note = message.text
    value = (await state.get_data())["rating"]
    user_id = message.from_user.id
    try:
        obj = MentalHealth(userId=user_id, rating=value, note=note)
        db_session.add(obj)
        db_session.commit()
        asyncio.gather(
            send_message(message, "✅ Спасибо, что ввели данные!\n📊 Не забывайте — вы всегда можете попросить у меня график с вашими данными для удобного отслеживания."),
            state.clear()
        )
    except BaseException as ex:
        print(ex)
        asyncio.gather(
            send_message(message, "Произошла ошибка при сохранении данных. Пожалуйста, введите заметку заново."),
            state.set_state(MentalStates.ask_to_enter)
        )
