import io
import uuid
from PIL import Image, ImageFile
from aiogram import types
from aiogram import Bot
from aiogram.types import BufferedInputFile
from io import BytesIO
from aiogram.types import Message

MAX_MESSAGE_LENGTH = 4096

async def send_long_message(bot: Bot, chat_id: int, text: str, parse_mode="Markdown"):
    chunks = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    for chunk in chunks:
        await bot.send_message(chat_id=chat_id, text=chunk, parse_mode=parse_mode)


async def convert_to_image(photo, bot: Bot) -> ImageFile.ImageFile:
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    fp = io.BytesIO()
    await bot.download_file(file_path, fp)

    pil_image = Image.open(fp)
    pil_image = pil_image.convert("RGB")
    return pil_image


async def send_message(message: types.Message, text, *args, **kwargs):
    await message.answer(text, *args, **kwargs)


async def send_image(bot: Bot, chat_id: int, img: Image.Image, caption=None):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    file = BufferedInputFile(buffer.read(), filename=str(uuid.uuid4()) + ".png")
    await bot.send_photo(chat_id, photo=file, caption=caption)
