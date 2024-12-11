import aiogram
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import *
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime, timedelta

from admin import add_action_to_db, get_active_actions, set_vote
from bot import dp, bot
from models import Action, DateError
from config import ADMIN_IDS
from keyboards import main_menu_keyboard
from states import AddActionStates


async def actions(message: Message, state: FSMContext):

    await state.clear()

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

    kb = ReplyKeyboardBuilder()

    back_button = KeyboardButton(text='К мероприятиям ↩️')

    kb.add(back_button)

    await message.answer('Введите название мероприятия: ', reply_markup=kb.as_markup(resize_keyboard=True))

    await state.set_state(AddActionStates.action_name)


async def add_action_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer(
        'Теперь введите дату мероприятия в формате ДД.ММ.ГГГГ или частоту мероприятия '
        '(например, <b>19.12.2025</b> или <b>Каждую пятницу</b>): '
    )

    await state.set_state(AddActionStates.action_date)


async def add_action_date(message: Message, state: FSMContext):

    now = datetime.now()
    time = None
    try:
        time = datetime.strptime(message.text, '%d.%m.%Y')
        if time < now:
            raise DateError('Дата уже прошла!\n\nПопробуйте еще раз ввести дату:')
    except ValueError:
        if ''.join(message.text.split('.')).isdigit():
            await message.answer('Неверный формат даты, попробуйте еще раз '
                                 '(например, <b>19.12.2025</b> или <b>Каждую пятницу</b>):')
            await state.set_state(AddActionStates.action_date)
            return
    except DateError:
        await message.answer('Мы сами очень расстроены, но эта дата уже прошла 😔\n\n'
                             'Попробуйте ввести дату еще раз:')
        await state.set_state(AddActionStates.action_date)
        return

    if isinstance(time, datetime):
        time = min(time - timedelta(days=1), now + timedelta(days=10))
    else:
        time = now + timedelta(days=10)

    await state.update_data(start=now.strftime("%d-%m-%Y %H:%M:%S"))
    await state.update_data(end=time.strftime("%d-%m-%Y %H:%M:%S"))

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
        'contact': data["contact"],
        'status': 'pending',
        "creator": feedback.from_user.id,
        "votes_favor": [],
        "votes_against": [],
        "start": str(data["start"]),
        "end": str(data["end"])
    }

    add_action_to_db(data["name"], action)

    notice_text = f'''<b>Предложено новое мероприятие:</b>

<b>Название:</b> {data["name"]}
<b>Дата:</b> {data["date"]}

<b>Описание:</b> {data["description"]}

<b>Контакт для связи:</b> {data["contact"]}'''

    admin_kb = InlineKeyboardBuilder()

    approve = InlineKeyboardButton(
        text='Принять ✅',
        callback_data='approve_action'
    )

    deny = InlineKeyboardButton(
        text='Отклонить ❌',
        callback_data='deny_action'
    )

    admin_kb.row(approve, deny, width=1)

    for id in ADMIN_IDS:
        await bot.send_message(id, notice_text, reply_markup=admin_kb.as_markup())

    await feedback.answer(
        'Готово! После модерации ваше предложение будет опубликовано и допущено к голосованию',
        reply_markup=main_menu_keyboard().as_markup(resize_keyboard=True)
    )


async def active_actions_list(feedback: Message | CallbackQuery):

    kb = InlineKeyboardBuilder()

    btn_favor = InlineKeyboardButton(
        text=f'За () 👍',
        callback_data='action_favor'
    )

    btn_against = InlineKeyboardButton(
        text=f'Против () 👎',
        callback_data='action_against'
    )

    btn_next = InlineKeyboardButton(
        text='Дальше ➡️',
        callback_data='next_actions'
    )

    btn_prev = InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data='prev_actions'
    )
    kb.row(btn_favor, btn_against, width=2)
    if len(get_active_actions()) > 1:
        kb.row(btn_next, width=1)

    current_index = 0
    if isinstance(feedback, CallbackQuery):
        current_index = int(feedback.message.text[feedback.message.text.index('(') + 1]) - 1

    if not get_active_actions():
        await feedback.answer('Сейчас нет предложенных мероприятий 😔🥀‍')
    elif isinstance(feedback, Message):
        action_list = get_active_actions()
        action = Action(action_list[0]["name"])

        action_info = f'''<b>{action.name}</b> (1/{len(action_list)})

Дата проведения: {action.date}

Описание мероприятия: {action.description}'''

        btn_favor.text = f'За ({len(action.votes_favor)}) 👍'
        btn_against.text = f'Против ({len(action.votes_against)}) 👎'

        await feedback.answer(action_info, reply_markup=kb.as_markup())

    elif isinstance(feedback, CallbackQuery):

        if feedback.data == 'prev_actions':

            current_index -= 1

            action_list = get_active_actions()
            action = Action(action_list[current_index]["name"])

            action_info = f'''<b>{action.name}</b> ({current_index + 1}/{len(action_list)})

Дата проведения: {action.date}

Описание мероприятия: {action.description}'''

            kb = InlineKeyboardBuilder()

            if len(get_active_actions()) == 1:
                kb.row(btn_favor, btn_against, width=2)
            elif current_index == 0:
                kb.row(btn_favor, btn_against, btn_next, width=2)
            elif current_index == len(get_active_actions()) - 1:
                kb.row(btn_favor, btn_against, btn_prev, width=2)
            else:
                kb.row(btn_favor, btn_against, btn_prev, btn_next, width=2)

            btn_favor.text = f'За ({len(action.votes_favor)}) 👍'
            btn_against.text = f'Против ({len(action.votes_against)}) 👎'

            await feedback.message.edit_text(action_info, reply_markup=kb.as_markup())

        elif feedback.data == 'next_actions':

            current_index += 1

            action_list = get_active_actions()

            action = Action(action_list[current_index]["name"])

            action_info = f'''<b>{action.name}</b> ({current_index + 1}/{len(action_list)})

Дата проведения: {action.date}

Описание мероприятия: {action.description}'''

            kb = InlineKeyboardBuilder()

            if len(get_active_actions()) == 1:
                kb.row(btn_favor, btn_against, width=2)
            elif current_index == 0:
                kb.row(btn_favor, btn_against, btn_next, width=2)
            elif current_index == len(get_active_actions()) - 1:
                kb.row(btn_favor, btn_against, btn_prev, width=2)
            else:
                kb.row(btn_favor, btn_against, btn_prev, btn_next, width=2)

            btn_favor.text = f'За ({len(action.votes_favor)}) 👍'
            btn_against.text = f'Против ({len(action.votes_against)}) 👎'

            await feedback.message.edit_text(action_info, reply_markup=kb.as_markup())


async def vote_action(call: CallbackQuery):

    await call.answer('Спасибо! Ваш голос учтён. Чтобы переголосовать, просто отметьте другой вариант.')

    vote = True if call.data == 'action_favor' else False

    name = call.message.text.split('(')[0].strip()
    set_vote('actions', name, call.from_user.id, vote=vote)

    action_list = get_active_actions()
    current_index = int(call.message.text[call.message.text.index('(') + 1]) - 1
    action = Action(action_list[current_index]["name"])

    btn_favor = InlineKeyboardButton(
        text=f'За ({len(action.votes_favor)}) 👍',
        callback_data='action_favor'
    )

    btn_against = InlineKeyboardButton(
        text=f'Против ({len(action.votes_against)}) 👎',
        callback_data='action_against'
    )

    btn_next = InlineKeyboardButton(
        text='Дальше ➡️',
        callback_data='next_actions'
    )

    btn_prev = InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data='prev_actions'
    )

    kb = InlineKeyboardBuilder()

    if len(get_active_actions()) == 1:
        kb.row(btn_favor, btn_against, width=2)
    elif current_index == 0:
        kb.row(btn_favor, btn_against, btn_next, width=2)
    elif current_index == len(get_active_actions()) - 1:
        kb.row(btn_favor, btn_against, btn_prev, width=2)
    else:
        kb.row(btn_favor, btn_against, btn_prev, btn_next, width=2)

    try:
        await call.message.edit_reply_markup(reply_markup=kb.as_markup())
    except aiogram.exceptions.TelegramBadRequest as err:
        print(err)


def register_handlers_actions():

    dp.message.register(actions, lambda message: message.text in ['Мероприятия 📌', 'К мероприятиям ↩️'])

    dp.message.register(add_action, F.text == 'Предложить мероприятие 💬')
    dp.message.register(add_action_name, StateFilter(AddActionStates.action_name))
    dp.message.register(add_action_date, StateFilter(AddActionStates.action_date))
    dp.message.register(add_action_descriprion, StateFilter(AddActionStates.action_description))
    dp.callback_query.register(add_action_contact, F.data == 'skip_contact_actions')
    dp.message.register(add_action_contact, StateFilter(AddActionStates.contact))

    dp.message.register(active_actions_list, F.text == 'Голосования 📊')
    dp.callback_query.register(active_actions_list, lambda call: call.data in ['next_actions', 'prev_actions'])

    dp.callback_query.register(vote_action, lambda call: call.data in ['action_favor', 'action_against'])

