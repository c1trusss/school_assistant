from aiogram import F
from aiogram.types import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import dp


async def school(message: Message):

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


def register_handlers_school():
    dp.message.register(school, F.text == 'Школа 🏫')



