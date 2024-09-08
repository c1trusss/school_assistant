import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: Message):

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

    await message.answer(f'{greeting}! Этот бот поможет вам освоится в новой школе или чувствовать увереннее в привычной обстановке')


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
