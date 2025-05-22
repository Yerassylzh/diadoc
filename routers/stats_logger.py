import asyncio
from datetime import datetime, timedelta

from aiogram import Router, types, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.db import db_session
from db.models import Glucose, PhysicalHealth, MentalHealth, Diet
from utils.base import send_long_message, send_message
from db.db import db_session
from utils.stats_diet import get_calories_consumed_plot_image
from utils.stats_glucose import get_glucose_plot_image
from utils.stats_sport import get_calories_plot_image
from utils.stats_mental import get_mental_wellness_plot_image
from utils.base import send_image


router = Router()

class StatStates(StatesGroup):
    ask_to_enter = State()

class StatTypes:
    SPORT = 0
    MENTAL = 1
    SUGAR = 2
    DIET = 3


class StatTypeCallback(CallbackData, prefix="stat_type"):
    value: int


class StatPeriodCallback(CallbackData, prefix="stat_period"):
    value: int


def create_inlinekeyboard(*buttons: list[tuple[str, any]]):
    builder = InlineKeyboardBuilder()
    for text, data in buttons:
        builder.button(text=text, callback_data=data)
    return builder.adjust(1).as_markup()


@router.message(Command(commands=["log_stats"]))
async def handle_start(message: types.Message, state: FSMContext):
    keyboard = create_inlinekeyboard(
        ("Физические активности", StatTypeCallback(value=StatTypes.SPORT)),
        ("Ментальное здоровье", StatTypeCallback(value=StatTypes.MENTAL)),
        ("Уровень сахара", StatTypeCallback(value=StatTypes.SUGAR)),
        ("Питание", StatTypeCallback(value=StatTypes.DIET))
    )
    await message.answer("Пожалуйста, введите параметр, по которому отобразить статистику", reply_markup=keyboard)


@router.callback_query(StatTypeCallback.filter())
async def handle_stattype(
    callback: CallbackQuery,
    callback_data: StatTypeCallback,
    state: FSMContext
):
    await state.update_data({"stat_type": callback_data.value})
    keyboard = create_inlinekeyboard(
        ("За сегодня", StatPeriodCallback(value=1)),
        ("За последнюю неделю", StatPeriodCallback(value=7)),
        ("Ввести вручную", StatPeriodCallback(value=-1)) # flag
    )
    await callback.message.answer("Пожалуйста, введите период времени, по которому вывести график", reply_markup=keyboard)


@router.callback_query(StatPeriodCallback.filter(F.value == -1))
async def handle_manual_enter(
    callback: CallbackQuery,
    callback_data: StatPeriodCallback,
    state: FSMContext
):
    await callback.message.answer("Пожалуйста, введите период, по которому хотите увидеть статистику")
    await state.set_state(StatStates.ask_to_enter)


@router.callback_query(StatPeriodCallback.filter(F.value != -1))
async def handle_choice_enter(
    callback: CallbackQuery,
    callback_data: StatPeriodCallback,
    state: FSMContext
):
    stat_type = (await state.get_data())["stat_type"]
    await callback.message.answer("Пожалуйста, подождите пока ваши данные генерируются")
    await send_stats(period=callback_data.value, user_id=callback.from_user.id, bot=callback.bot, stat_type=stat_type)


@router.message(StateFilter(StatStates.ask_to_enter))
async def handle_enter(message: types.Message, state: FSMContext):
    period = message.text
    if not validate_period(period):
        await asyncio.gather(
            send_message(message, "Вы неправильно ввели период. Это значение должно быть положительным челым числом. Пожалуйста, введите его обратно"),
            state.set_state(StatStates.ask_to_enter)
        )
        return

    stat_type = (await state.get_data())["stat_type"]
    await message.answer("Пожалуйста, подождите пока ваши данные генерируются")
    await send_stats(period=int(period), user_id=message.from_user.id, bot=message.bot, stat_type=stat_type)
    await state.clear()


def validate_period(value):
    try:
        value = int(value)
        return value >= 1
    except BaseException as ex:
        return False


async def send_stats(period: int, user_id: int, bot: Bot, stat_type: StatTypes) -> None:
    img, async_task = get_stats_img(bot, user_id, stat_type, period)
    await send_image(bot, user_id, img, caption=f"Вот ваша статистика на последние {period} дней") 
    if async_task:
        await async_task


def get_stats_img(bot: Bot, chat_id: int, stat_type: StatTypes, period: int):
    user_id = chat_id
    
    spec_date = datetime.now() - timedelta(days=period)

    img = None
    async_task = None

    if stat_type == StatTypes.SUGAR:
        model = Glucose
        stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
        img = get_glucose_plot_image(stats)

    elif stat_type == StatTypes.SPORT:
        model = PhysicalHealth
        stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
        img = get_calories_plot_image(stats)

    elif stat_type == StatTypes.MENTAL:
        model = MentalHealth
        stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
        img = get_mental_wellness_plot_image(stats)
        msg = "**Заметки**\n"
        for data in stats:
            msg += (
                "\n"
                f"**Дата**: {data.createdAt.strftime("%d-%m-%Y")}\n"
                f"**Заметка**: {data.note}\n"
            )
        async_task = send_long_message(bot, chat_id, msg)

    else:
        model = Diet
        stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
        img = get_calories_consumed_plot_image(stats)

    return img, async_task
