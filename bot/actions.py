from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import *
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from admin import add_action_to_db
from bot import dp
from keyboards import main_menu_keyboard
from states import AddActionStates


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


async def add_action(message: Message, state: FSMContext):

    kb = ReplyKeyboardRemove()

    await message.answer('Введите название мероприятия: ', reply_markup=kb)

    await state.set_state(AddActionStates.action_name)


async def add_action_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer('Теперь введите дату мероприятия в формате ДД.ММ.ГГГГ: ')

    await state.set_state(AddActionStates.action_date)


async def add_action_date(message: Message, state: FSMContext):

    await state.update_data(date=message.text)

    await message.answer('Теперь введите описание мероприятия: ')

    await state.set_state(AddActionStates.action_description)


async def add_action_descriprion(message: Message, state: FSMContext):

    await state.update_data(description=message.text)

    data = await state.get_data()

    await state.clear()

    action = {
        'date': data["date"],
        'description': data["description"],
        'status': 'pending'
    }

    add_action_to_db(data["name"], action)

    # ToDo: отправить уведомление админам

    await message.answer('Готово!', reply_markup=main_menu_keyboard().as_markup(resize_keyboard=True))


def register_handlers_actions():
    dp.message.register(actions, F.text == 'Мероприятия 📌')
    dp.message.register(add_action, F.text == 'Предложить мероприятие 💬')
    dp.message.register(add_action_name, StateFilter(AddActionStates.action_name))
    dp.message.register(add_action_date, StateFilter(AddActionStates.action_date))
    dp.message.register(add_action_descriprion, StateFilter(AddActionStates.action_description))
