from datetime import datetime, timedelta
import io
import os
from PIL import Image, ImageFile
import pytz
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot
from babel.dates import get_timezone_location


def get_keyboard_buttons(data: list[str], in_row=1):
    """Returs a keyboard, with 'row' buttons in each row"""

    buttons = []
    for text in data:
        if len(buttons) == 0 or len(buttons[-1]) == in_row:
            buttons.append([KeyboardButton(text=text)])
        else:
            buttons[-1].append(KeyboardButton(text=text))

    return buttons


async def convert_to_image(photo, bot: Bot) -> ImageFile.ImageFile:
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    fp = io.BytesIO()
    await bot.download_file(file_path, fp)

    pil_image = Image.open(fp)
    pil_image = pil_image.convert("RGB")
    return pil_image


def get_week_start() -> datetime:
    now = datetime.now()
    nw = datetime(now.year, now.month, now.day, 1, 0, 0)

    while nw.weekday() != 0:
        nw -= timedelta(days=1)

    return nw
