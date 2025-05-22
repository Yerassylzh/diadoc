import asyncio
from datetime import datetime, timedelta
import os
import uuid

from aiogram import Router, types, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile

from db.db import db_session
from db.models import Glucose, PhysicalHealth, MentalHealth, Diet
from utils.base import send_long_message, send_message
from db.db import db_session
from utils.pdf_builder import PDFBuilder
from utils.stats_diet import get_calories_consumed_plot_image
from utils.stats_glucose import get_glucose_plot_image
from utils.stats_sport import get_calories_plot_image
from utils.stats_mental import get_mental_wellness_plot_image
from utils.base import send_image

router = Router()

class ExportStates(StatesGroup):
    ask_to_enter = State()


class ExportPeriodCallback(CallbackData, prefix="export_period"):
    value: int


def create_inlinekeyboard(*buttons: list[tuple[str, any]]):
    builder = InlineKeyboardBuilder()
    for text, data in buttons:
        builder.button(text=text, callback_data=data)
    return builder.adjust(1).as_markup()


@router.message(Command(commands=["export_all"]))
async def handle_start(message: types.Message, state: FSMContext):
    keyboard = create_inlinekeyboard(
        ("За сегодня", ExportPeriodCallback(value=1)),
        ("За последнюю неделю", ExportPeriodCallback(value=7)),
        ("Ввести вручную", ExportPeriodCallback(value=-1)) # flag
    )
    await message.answer("Пожалуйста, введите период времени, по которому вы хотите экспортировать данные", reply_markup=keyboard)


@router.callback_query(ExportPeriodCallback.filter(F.value == -1))
async def handle_manual_enter(
    callback: CallbackQuery,
    callback_data: ExportPeriodCallback,
    state: FSMContext
):
    await callback.message.answer("Пожалуйста, введите период, по которому хотите увидеть статистику")
    await state.set_state(ExportStates.ask_to_enter)


@router.callback_query(ExportPeriodCallback.filter(F.value != -1))
async def handle_choice_enter(
    callback: CallbackQuery,
    callback_data: ExportPeriodCallback,
    state: FSMContext
):
    await callback.message.answer("Пожалуйста, подождите пока ваши данные генерируются...")
    await send_pdf(period=callback_data.value, user_id=callback.from_user.id, bot=callback.bot)


@router.message(StateFilter(ExportStates.ask_to_enter))
async def handle_enter(message: types.Message, state: FSMContext):
    period = message.text
    if not validate_period(period):
        await asyncio.gather(
            send_message(message, "Вы неправильно ввели период. Это значение должно быть положительным челым числом. Пожалуйста, введите его обратно"),
            state.set_state(ExportStates.ask_to_enter)
        )
        return

    await message.answer("Пожалуйста, подождите пока ваши данные генерируются...")
    await send_pdf(period=int(period), user_id=message.from_user.id, bot=message.bot)
    await state.clear()


def validate_period(value):
    try:
        value = int(value)
        return value >= 1
    except BaseException as ex:
        return False


def get_glucose_img(spec_date, user_id):
    model = Glucose
    stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
    img = get_glucose_plot_image(stats)
    return img


def get_sport_img(spec_date, user_id):
    model = PhysicalHealth
    stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
    img = get_calories_plot_image(stats)
    return img


def get_mental_data(spec_date, user_id):
    model = MentalHealth
    stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
    img = get_mental_wellness_plot_image(stats)
    msg = "Заметки\n"
    for data in stats:
        msg += (
            "\n"
            f"Дата: {data.createdAt.strftime("%d-%m-%Y")}\n"
            f"Заметка: {data.note}\n"
        )
    
    return img, msg


def get_diet_image(spec_date, user_id):
    model = Diet
    stats = db_session.query(model).filter(model.userId == user_id).filter(model.createdAt >= spec_date).all()
    img = get_calories_consumed_plot_image(stats)
    return img

    
async def send_pdf(period: int, user_id: int, bot: Bot):
    spec_date = datetime.now() - timedelta(days=period)

    output_path = str(uuid.uuid4()) + ".pdf"
    pdf_builder = PDFBuilder(output_path)
    pdf_builder.add_text(f"Этот файл содержить все данные за последние {period} дней.")
    pdf_builder.add_image(get_glucose_img(spec_date, user_id))
    pdf_builder.add_image(get_sport_img(spec_date, user_id))
    pdf_builder.add_image(get_diet_image(spec_date, user_id))
    img, msg = get_mental_data(spec_date, user_id)
    pdf_builder.add_image(img)
    pdf_builder.add_text(msg)
    pdf_builder.save()

    pdf_file = FSInputFile(output_path, filename="report.pdf")
    await bot.send_document(chat_id=user_id, document=pdf_file, caption="📄 Вот ваш отчёт!")
    os.remove(output_path)
