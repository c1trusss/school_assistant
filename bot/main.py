import asyncio
from datetime import datetime
import json
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import *
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import default_state

from actions import register_handlers_actions
from admin import add_user, register_handlers_admin
from bot import bot, dp
from config import TOKEN
from keyboards import *
from petitions import register_handlers_petitions
from school import register_handlers_school


@dp.message(
    lambda message: message.text in ['/start', 'Назад', 'Меню', 'Главное меню', 'Назад ↩️'],
    StateFilter(default_state)
)
async def start(message: Message, state: FSMContext):

    await state.clear()

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

# Функции администратора
register_handlers_admin()

# Мероприятия
register_handlers_actions()

# Петиции
register_handlers_petitions()

# Школа
register_handlers_school()


if __name__ == '__main__':
    logging.warning('BOT POLLING')
    logging.warning('TG: @sviblovo_school_bot')
    logging.warning('BOT POLLING')
    dp.run_polling(bot, skip_updates=True)
