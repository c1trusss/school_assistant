import asyncio
from datetime import datetime
import json
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import *
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command

from actions import register_handlers_actions
from admin import add_user
from bot import bot, dp
from config import TOKEN
from keyboards import *


@dp.message(lambda message: message.text in ['/start', 'Назад', 'Меню', 'Главное меню', 'Назад ↩️'])
async def start(message: Message):

    user_id = message.from_user.id
    name = message.from_user.username

    add_user(user_id, name)

    greeting = ''
    match datetime.now().hour:
        case 0 | 1 | 2 | 3 | 4:
            greeting = 'Доброй ночи'
        case 5 | 6 | 7 | 8 | 9 | 10 | 11:
            greeting = 'Доброе утро'
        case 12 | 13 | 14 | 15 | 16:
            greeting = 'Добрый день'
        case 17 | 18 | 19 | 20 | 21 | 22 | 23:
            greeting = 'Добрый вечер'

    await message.answer(
        f'{greeting}! Этот бот поможет вам освоится в новой школе или чувствовать себя увереннее в привычной '
        f'обстановке',
        reply_markup=main_menu_keyboard().as_markup(resize_keyboard=True)
    )


# Мероприятия
register_handlers_actions()


@dp.message(F.text == 'Школа 🏫')
async def school_menu(message: Message):

    lessons_button = KeyboardButton(text='Расписание уроков 📆')
    rings_button = KeyboardButton(text='Расписание звонков 🔔')
    food_button = KeyboardButton(text='Столовая 🍽️')
    main_menu_button = KeyboardButton(text='Назад ↩️')

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        lessons_button,
        rings_button,
        food_button,
        main_menu_button,
        width=1
    )

    await message.answer(
        'Это раздел с жизнью школы. Здесь вы можете узнать расписание уроков, звонков, а так же меню '
        'в школьной столовой',
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


if __name__ == '__main__':
    logging.warning('BOT POLLING')
    logging.warning('TG: @sviblovo_school_bot')
    logging.warning('BOT POLLING')
    dp.run_polling(bot, skip_updates=True)
