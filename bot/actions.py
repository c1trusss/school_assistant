from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import *
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from admin import add_action_to_db
from bot import dp, bot
from config import ADMIN_IDS
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

    await message.answer(
        'Теперь введите дату мероприятия в формате ДД.ММ.ГГГГ или частоту мероприятия '
        '(например, <b>19.12.2025</b> или <b>Каждую пятницу</b>: '
    )

    await state.set_state(AddActionStates.action_date)


async def add_action_date(message: Message, state: FSMContext):

    await state.update_data(date=message.text)

    await message.answer('Теперь введите описание мероприятия: ')

    await state.set_state(AddActionStates.action_description)


async def add_action_descriprion(message: Message, state: FSMContext):

    await state.update_data(description=message.text)

    keyboard = InlineKeyboardBuilder()

    skip_button = InlineKeyboardButton(
        text='Пропустить',
        callback_data='skip_contact_actions'
    )

    keyboard.add(skip_button)

    await message.answer('Оставьте контакт для связи (необязательно): ', reply_markup=keyboard.as_markup())

    await state.set_state(AddActionStates.contact)


async def add_action_contact(feedback: Message, state: FSMContext):

    if isinstance(feedback, Message):
        await state.update_data(contact=feedback.text)
    elif isinstance(feedback, CallbackQuery):
        await state.update_data(contact='-')

    data = await state.get_data()

    await state.clear()

    action = {
        'date': data["date"],
        'description': data["description"],
        'status': 'pending'
    }

    add_action_to_db(data["name"], action)

    notice_text = f'''<b>Предложено новое мероприятие:</b>

<b>Название:</b> {data["name"]}
<b>Дата:</b> {data["date"]}

<b>Описание:</b> {data["description"]}

<b>Контакт для связи:</b> {data["contact"]}'''

    for id in ADMIN_IDS:
        await bot.send_message(id, notice_text)

    await feedback.answer(
        'Готово! После модерации ваше предложение будет опубликовано и допущено к голосованию',
        reply_markup=main_menu_keyboard().as_markup(resize_keyboard=True)
    )


def register_handlers_actions():

    dp.message.register(actions, F.text == 'Мероприятия 📌')

    dp.message.register(add_action, F.text == 'Предложить мероприятие 💬')
    dp.message.register(add_action_name, StateFilter(AddActionStates.action_name))
    dp.message.register(add_action_date, StateFilter(AddActionStates.action_date))
    dp.message.register(add_action_descriprion, StateFilter(AddActionStates.action_description))
    dp.callback_query.register(add_action_contact, F.data == 'skip_contact_actions')
    dp.message.register(add_action_contact, StateFilter(AddActionStates.contact))
