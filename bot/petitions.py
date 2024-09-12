from aiogram import F
from aiogram.types import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import dp


async def petitions(message: Message):

    await message.answer('Это меню с петициями')


def register_handlers_petitions():
    dp.message.register(petitions, F.text == 'Петиции 📝')
