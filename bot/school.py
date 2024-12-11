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


async def rings(message: Message):

    kb = ReplyKeyboardBuilder()

    back_button = KeyboardButton(text='Назад ↩️')

    kb.add(back_button)

    await message.answer('Здесь вы можете ознакомиться с расписанием звонков. ',
                         reply_markup=kb.as_markup(resize_keyboard=True))
    await message.answer(f'''
1 урок: 8:30 - 9:15
перемена: 9:15 - 9:25 (10 минут)
2 урок: 9:25 - 10:10
перемена: 10:10 - 10:30 (20 минут)
3 урок: 10:30 - 11:15
перемена: 11:15 - 11:35 (20 минут)
4 урок: 11:35 - 12:20
перемена 12:20 - 12:30 (10 минут)
5 урок: 12:30 - 13:15
перемена: 13:15 - 13:30 (15 минут)
6 урок: 13:30 - 14:15
перемена: 14:15 - 14:30 (15 минут)
7 урок: 14:30 - 15:15
перемена: 15:15 - 15:45 (30 минут)
далее внеурочная деятельность''', reply_markup=kb.as_markup(resize_keyboard=True))



async def lessons(message: Message):

    kb = ReplyKeyboardBuilder()

    back_button = KeyboardButton(text='Назад ↩️')

    kb.add(back_button)

    await message.answer('В каком вы классе?', reply_markup=kb.as_markup(resize_keyboard=True))

    kb1 = ReplyKeyboardBuilder()

    back_button1 = KeyboardButton(text='Назад ↩️')
    buttons = [KeyboardButton(text=str(i)) for i in range(5, 12)]

    kb1.add(back_button1, *buttons)

    await message.answer('Выберите букву класса:', reply_markup=kb.as_markup(resize_keyboard=True))


async def main_menu(message: Message):

    await message.answer('Здесь вы можете ознакомиться с меню столовой.')

    kb = ReplyKeyboardBuilder()
    buttons_text = ['Назад ↩️', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    buttons = [KeyboardButton(text=btn_text) for btn_text in buttons_text]
    kb.add(*buttons)

    await message.answer('Выберите день недели:', reply_markup=kb.as_markup(resize_keyboard=True))


async def monday(message1: Message):
    kb_ = ReplyKeyboardBuilder()

    back_button_ = KeyboardButton(text='Назад ↩️')

    kb_.add(back_button_)

    await message1.answer(f'''
1 варинт:

ЗАВТРАК:

ОБЕД:

''', reply_markup=kb_.as_markup(resize_keyboard=True))

    await message1.answer(f'''
2 вариант:

ЗАВТРАК:
- блинчики

ОБЕД:
- ёжики куриные
- изделия макаронные отварные
- чай
- смородиновый компот
''', reply_markup=kb_.as_markup(resize_keyboard=True))


async def tuesday(message1: Message):
    kb_ = ReplyKeyboardBuilder()

    back_button_ = KeyboardButton(text='Назад ↩️')

    kb_.add(back_button_)

    await message1.answer(f'''
1 вариант:

ЗАВТРАК:

ОБЕД:
''', reply_markup=kb_.as_markup(resize_keyboard=True))

    await message1.answer(f'''
2 вариант:

ЗАВТРАК:
- гречка отварная
- фрикадельки по-калининградски

ОБЕД:
- рис отварной
- говядина по-мексикански
- чай
- яблочный компот
''', reply_markup=kb_.as_markup(resize_keyboard=True))


async def wednesday(message1: Message):
    kb_ = ReplyKeyboardBuilder()

    back_button_ = KeyboardButton(text='Назад ↩️')

    kb_.add(back_button_)

    await message1.answer(f'''
1 вариант:

ЗАВТРАК:
- каша гречневая с молоком
- круассан
ОБЕД:

- картофель отварной
- азу по-татарски
- чай
- апельсиновый компот
''', reply_markup=kb_.as_markup(resize_keyboard=True))

    await message1.answer(f'''
2 вариант:

ЗАВТРАК:
- омлет
- пицца

ОБЕД:
- картофель запеченный по-домашнему
- наггетсы
- чай
''', reply_markup=kb_.as_markup(resize_keyboard=True))


async def thursday(message1: Message):
    kb_ = ReplyKeyboardBuilder()

    back_button_ = KeyboardButton(text='Назад ↩️')

    kb_.add(back_button_)

    await message1.answer(f'''
1 вариант:

ЗАВТРАК:
- наггетсы
- изделия макаронные отварные

ОБЕД:
- плов мясной
- чай
- клюквенный компот
''', reply_markup=kb_.as_markup(resize_keyboard=True))

    await message1.answer(f'''
2 вариант:

ЗАВТРАК:
- пирожок с клубничным джемом
- творог
- хлопья сладкие с молоком

ОБЕД:
- пельмени отварные
- чай
- апельсиновый компот
''', reply_markup=kb_.as_markup(resize_keyboard=True))


async def friday(message1: Message):
    kb_ = ReplyKeyboardBuilder()

    back_button_ = KeyboardButton(text='Назад ↩️')

    kb_.add(back_button_)

    await message1.answer(f'''
1 вариант:

ЗАВТРАК:
- запеканка из творога
- яблоки

ОБЕД:
- гречка отварная
- митболы
''', reply_markup=kb_.as_markup(resize_keyboard=True))

    await message1.answer(f'''
2 вариант:

ЗАВТРАК:
- сырники
- мандарин

ОБЕД:
- изделия макаронные отварные с соусом Альфредо
- чай
- напиток из сухофруктов
''', reply_markup=kb_.as_markup(resize_keyboard=True))


def register_handlers_school():
    dp.message.register(school, F.text == 'Школа 🏫')
    dp.message.register(rings, F.text == 'Расписание звонков 🔔')
    dp.message.register(lessons, F.text == 'Расписание уроков 📆')
    dp.message.register(main_menu, F.text == 'Столовая 🍽️')
    dp.message.register(monday, F.text == 'Понедельник')
    dp.message.register(tuesday, F.text == 'Вторник')
    dp.message.register(wednesday, F.text == 'Среда')
    dp.message.register(thursday, F.text == 'Четверг')
    dp.message.register(friday, F.text == 'Пятница')




