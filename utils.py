from aiogram import types


async def send_message(message: types.Message, text, *args, **kwargs):
    await message.answer(text, *args, **kwargs)
