from datetime import datetime
import json
from typing import Literal

from aiogram import F
from aiogram.types import CallbackQuery

from bot import dp, bot
from models import Action


def add_user(id: int, name: str) -> bool:

    """
    Добавляет пользователя в базу

    В качестве аргументов принимает:

    1. id - id пользователя (message.from_user.id)

    2. name - имя пользователя (message.from_user.username)

    В результате добавляет пользователя в файл users.json
    """

    user_exist = False

    user = {
        "name": name,
        "account_created": '-'.join((str(datetime.now().date())).split('-')[::-1]),
        "admin": "False",
        "sub": "True",
    }

    with open("users.json", 'r', encoding='utf8') as file:
        data = json.load(file)
        if str(id) not in data:
            data[str(id)] = user
        else:
            user_exist = True

    with open("users.json", 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)

    return user_exist


def add_action_to_db(name: str, description: dict):

    with open('actions.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    data[name] = description

    with open('actions.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)


def change_status(file_type: Literal['action', 'petition'], name: str, status: str):

    """
    :param file_type: Тип активности
    :param name: Имя активности
    :param status: Новый статус активности
    :return: None
    """

    file_name = f'{file_type}s.json'

    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

    data[name]["status"] = status

    with open(file_name, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)


async def approve_action(call: CallbackQuery):

    data = call.message.text.strip().split()

    name = ' '.join(data[data.index('Название:') + 1:data.index('Дата:')])

    action = Action(name)

    match action.status:
        case 'pending':

            change_status('action', name, 'active')

            await call.answer('Мероприятие одобрено!')
            await bot.send_message(action.creator, 'Ваше предложение было одобрено!'
                                                   ' Вы можете проголосовать за него в разделе "Голосования".')

        case 'active':
            await call.answer('Это мероприятие уже одобрено!')
        case 'denied':
            await call.answer('Это мероприятие уже отклонено!')


async def deny_action(call: CallbackQuery):

    data = call.message.text.strip().split()

    name = ' '.join(data[data.index('Название:') + 1:data.index('Дата:')])

    action = Action(name)

    match action.status:
        case 'pending':

            change_status('action', name, 'denied')

            await call.answer('Мероприятие отклонено!')
            await bot.send_message(action.creator, 'К сожалению, ваше предложение было отклонено. За дополнительной '
                                                   'информацией обратитесь в Школьный Ученический Совет (ШУС)')

        case 'active':
            await call.answer('Это мероприятие уже одобрено!')
        case 'denied':
            await call.answer('Это мероприятие уже отклонено!')


def register_handlers_admin():

    dp.callback_query.register(approve_action, F.data == 'approve_action')
    dp.callback_query.register(deny_action, F.data == 'deny_action')

