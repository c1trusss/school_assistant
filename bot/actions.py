from aiogram.types import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import dp


async def actions(message: Message):

    active_votings_button = KeyboardButton(text='Голосования 📊')
    schedule_button = KeyboardButton(text='Расписание мероприятий 📆')
    ask_an_action_button = KeyboardButton(text='Предложить мероприятие 💬')
    back_button = KeyboardButton(text='Назад ↩️')

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        active_votings_button,
        schedule_button,
        ask_an_action_button,
        back_button,
        width=1
    )

    await message.answer(
        'Это меню мероприятий, здесь вы можете проголосовать за проведение мероприятия, предложить '
        'своё, а также посмотреть расписание уже запланированых активностей в школе.',
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


def register_handlers_actions():
    dp.message.register(actions, lambda message: message.text == 'Мероприятия 📌')