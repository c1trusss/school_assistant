from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keyboard():

    school_button = KeyboardButton(text='Школа 🏫')
    actions_button = KeyboardButton(text='Мероприятия 📌')
    account_button = KeyboardButton(text='Личный кабинет 👤')

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        school_button,
        actions_button,
        account_button,
        width=1
    )

    return keyboard
