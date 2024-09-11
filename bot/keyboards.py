from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keyboard():

    school_button = KeyboardButton(text='Школа 🏫')
    actions_button = KeyboardButton(text='Мероприятия 📌')
    petitions_button = KeyboardButton(text='Петиции 📝')

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        school_button,
        actions_button,
        petitions_button,
        width=1
    )

    return keyboard
