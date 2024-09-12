from aiogram import F
from aiogram.types import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import dp


async def petitions(message: Message):

    current_petitions_button = KeyboardButton(text='Актуальные петиции 📢')
    petitions_resulsts_button = KeyboardButton(text='Результаты петиций 📋')
    create_a_petition_button = KeyboardButton(text='Создать петицию ➕')
    back_button = KeyboardButton(text='Назад ↩️')

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        current_petitions_button,
        petitions_resulsts_button,
        create_a_petition_button,
        back_button,
        width=1
    )

    await message.answer('Это меню с петициями', reply_markup=keyboard.as_markup(resize_keyboard=True))


def register_handlers_petitions():
    dp.message.register(petitions, F.text == 'Петиции 📝')
