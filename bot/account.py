from aiogram import F
from aiogram.types import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import dp

import asyncio
from datetime import datetime

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State, StateFilter
from aiogram.types import Message, FSInputFile

import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from cryptography.fernet import Fernet

from models import *
from config import KEY


key = Fernet.generate_key()
cipher_suite = Fernet(KEY)

SCHEDULE = {
    0: [('Разговоры о важном', '8:30', '9:15'),
        ('ОБЗР', '9:25', '10:10'),
        ('Литература', '10:30', '11:15'),
        ('Физика', '11:35', '12:20'),
        ('Инженерный практикум', '12:30', '13:15'),
        ('Алгебра', '13:30', '14:15'),
        ('Геометрия', '14:30', '15:15')],
    1: [('Информатика', '8:30', '9:15'),
        ('История', '9:25', '10:10'),
        ('Русский язык', '10:30', '11:15'),
        ('Литература', '11:35', '12:20'),
        ('Алгебра', '12:30', '13:15'),
        ('Английский язык', '13:30', '14:15'),
        ('Химия', '14:30', '15:15'),
        ('Технологии современного производства', '15:30', '16:15')],
    2: [('Алгебра', '8:30', '9:15'),
        ('Русский язык', '9:25', '10:10'),
        ('Информатика', '10:30', '11:15'),
        ('Обществознание', '11:35', '12:20'),
        ('Вероятность и статистика', '12:30', '13:15'),
        ('География', '13:30', '14:15'),
        ('Физическая культура', '14:30', '15:15'),
        ('Технический английский', '15:30', '16:15')],
    3: [('Обществознание', '8:30', '9:15'),
        ('Физика', '9:25', '10:10'),
        ('Информатика', '10:30', '11:15'),
        ('Геометрия', '11:35', '12:20'),
        ('Английский язык', '12:30', '13:15'),
        ('Биология', '13:30', '14:15'),
        ('Физика', '14:30', '15:15')],
    4: [('Литература', '8:30', '9:15'),
        ('Алгебра', '9:25', '10:10'),
        ('Геометрия', '10:30', '11:15'),
        ('История', '11:35', '12:20'),
        ('Физика', '12:30', '13:15'),
        ('Инженерный практикум', '13:30', '14:15'),
        ('ВДАлиПр (Информатика)', '14:30', '15:15')]
}

todays_homeworks = {}


class RegisterStatesGroup(StatesGroup):
    login = State()
    password = State()


@dp.message(lambda msg: msg.text == "Личный кабинет 👤")
async def user_cabinet_command(message: Message):

    kb = ReplyKeyboardBuilder()

    buttons = [KeyboardButton(text=text) for text in ("Домашние задания", "Назад ↩️")]
    kb.row(*buttons, width=1)

    await message.answer('Вы вошли в личный кабинет', reply_markup=kb.as_markup(resize_keyboard=True))


@dp.message(Command('schedule'))
async def schedule_command(message: Message):
    weekday = datetime.now().weekday()

    if weekday in [5, 6]:
        schedule = 'Сегодня выходной, кумарим'
    else:
        schedule = f'Расписание на сегодня:\n\n'
        schedule += '\n'.join([f'{i + 1}. <b>{lesson[0]}</b> ({lesson[1]} - {lesson[2]})'
                               for i, lesson in enumerate(SCHEDULE[weekday])])

    await message.answer(schedule)


@dp.message(Command('next_lesson'))
async def next_lesson_command(message: Message):
    weekday = datetime.now().weekday()

    if weekday in [5, 6]:
        await message.answer('Сегодня выходной, кумарим')
        return
    else:
        today_schedule = SCHEDULE[weekday]
        next_lesson: tuple[str, str, str]
        for i, lesson in enumerate(today_schedule[:-1]):
            lesson_start = datetime.strptime(lesson[1], '%H:%M')
            if i == 0:
                if datetime.now().time() < lesson_start.time():
                    await message.answer(f"Уроки еще не начались\n\n"
                                         f"Первый урок: <b>{lesson[0]}</b> ({lesson[1]} - {lesson[2]})")
                    return
            lesson_next_start = datetime.strptime(today_schedule[i + 1][1], '%H:%M')
            if lesson_start.time() <= datetime.now().time() <= lesson_next_start.time():
                next_lesson = today_schedule[i + 1]
                break
        else:
            await message.answer('Домой')
            return

    if next_lesson[0] in (
            'Физическая культура',
            'Технологии современного производства',
            'Технический английский',
            'ВДАлиПр (Информатика)'
    ):
        await message.answer(f'Сдедующий урок <b>{next_lesson[0]}</b> ({next_lesson[1]} - {next_lesson[2]}), '
                             f'но можно и уйти домой')
        return

    await message.answer(f'Сдедующий урок:\n\n'
                         f'{today_schedule.index(next_lesson) + 1}. <b>{next_lesson[0]}</b> '
                         f'({next_lesson[1]} - {next_lesson[2]})')


@dp.message(Command('load_homework'))
async def load_hw_command(message: Message):

    driver = create_driver()
    user = User(message.from_user.id)

    msg = await message.answer('<b>Информация загружается...</b>')

    driver.get("https://school.mos.ru/")
    driver.set_window_size(1920, 1080)
    driver.set_window_position(0, 0)
    await asyncio.sleep(2)
    try:

        await msg.edit_text('<b>Захожу в МЭШ...</b>')
        while 1:
            try:
                log_in = driver.find_element(By.XPATH, ".//div[contains(@class, 'style_btn__3lIWs')]")
                log_in.click()
            except NoSuchElementException:
                break
            await asyncio.sleep(5)

        await msg.edit_text('<b>Авторизовываюсь...</b>')

        login = user.login
        password = cipher_suite.decrypt(user.password_hash).decode('utf8')

        driver.find_element(By.ID, "login").send_keys(login)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "bind").click()
        await asyncio.sleep(18)

        driver.fullscreen_window()

        # Удаление всех старых файлов с ДЗ
        for root, dirs, files in os.walk(os.curdir + "/files"):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)

        with open("homeworks.json", 'r', encoding='utf-8') as file:
            data = json.load(file)

        await msg.edit_text('<b>Открываю домашние задания...</b>')
        driver.save_screenshot(r"C:\Users\mythi\PycharmProjects\pythonProject\venv\screenshot1.png")
        driver.find_element(By.LINK_TEXT, "Задания").click()
        await asyncio.sleep(2)
        all_homeworks = {"last-update": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
        elem = driver.find_element(By.XPATH, ".//div[contains(@class, '1kkx4gx')]")
        days = elem.find_elements(By.XPATH, ".//div[contains(@class, 'homeworksForDayWrapper')]")
        for j in range(len(days)):
            elem = driver.find_element(By.XPATH, ".//div[contains(@class, 'diary-emotion-cache-1kkx4gx')]")
            day = elem.find_elements(By.XPATH, ".//div[contains(@class, 'homeworksForDayWrapper')]")[j]
            homeworks = {}
            date = (day
                    .find_element(By.XPATH, ".//div[contains(@class, 'dateAndCountOfHm')]")
                    .find_elements(By.XPATH, ".//p[contains(@class, 'E8taxZlPjqlq_tc1djmu')]"))[0].text.split()[1:]
            day_number = int(date[0])
            month = date[1]

            hw_date = f"{day_number} {month}"

            lessons = day.find_elements(By.XPATH, ".//div[contains(@class, 'homeworksForDay')]")

            for i in range(len(lessons)):
                driver.set_window_size(1920, 1080)
                elem = driver.find_element(By.XPATH, ".//div[contains(@class, 'diary-emotion-cache-1kkx4gx')]")
                day = elem.find_elements(By.XPATH, ".//div[contains(@class, 'homeworksForDayWrapper')]")[j]
                lesson = day.find_elements(By.XPATH, ".//div[contains(@class, 'homeworksForDay')]")[i]
                lesson_name = lesson.find_element(By.XPATH, ".//h6[contains(@class, 'DSXOGdoSiFGKohRuaDDx')]").text
                lesson_hw = lesson.find_element(By.XPATH, ".//div[contains(@class, 'descriptionBlock')]").text
                with open("blacklist.txt", 'r', encoding='cp1251') as f:
                    lines = f.readlines()
                    if lesson_name not in list(map(str.strip, lines)):
                        try:
                            await msg.edit_text(f'<b>Проверяю ДЗ на наличие файлов... ({hw_date}, {lesson_name})</b>')
                        except aiogram.exceptions.TelegramBadRequest:
                            pass
                        lesson.find_element(By.XPATH, ".//div[contains(@class, 'arrowLargeRightIcon')]").click()
                        await asyncio.sleep(4)
                        driver.find_element(By.XPATH, ".//div[contains(@class, '15i5qxa')]").click()
                        await asyncio.sleep(2)
                        driver.find_element(By.XPATH, ".//div[contains(@class, 'arrowIconBlock')]").click()
                        await asyncio.sleep(2)
                        try:
                            file = driver.find_element(By.XPATH, ".//p[contains(@class, 'bv6qar')]")
                            lesson_hw += f', file={file.text}'
                            file.click()
                            await asyncio.sleep(5)
                        except NoSuchElementException:
                            pass
                        finally:
                            await asyncio.sleep(2)
                            driver.back()
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, ".//div[contains(@class, 'homeworksForDay')]"))
                            )
                            await asyncio.sleep(2)

                homeworks[lesson_name] = lesson_hw

            all_homeworks[hw_date] = homeworks

        data[str(message.from_user.id)] = all_homeworks
        with open("homeworks.json", "w", encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

        await msg.edit_text("✅ <b>Готово! Домашние задания загружены!</b>")

    except Exception as e:
        print(e.__class__.__name__, e)
        await msg.edit_text(f'<b>Произошла ошибка на стороне сервера, попробуйте еще раз</b>')
    finally:
        driver.quit()


@dp.message(Command('homework'))
@dp.message(lambda msg: msg.text == "Домашние задания")
async def homework_command(message: Message):

    user = User(message.from_user.id)
    months = [
        'января',
        'февраля',
        'марта',
        'апреля',
        'мая',
        'июня',
        'июля',
        'августа',
        'сентября',
        'октября',
        'ноября',
        'декабря'
    ]

    with open("homeworks.json", "r", encoding='utf-8') as file:
        data = json.load(file)[str(user.id)]

        string = f'<b>Последнее обновление:</b> {data["last-update"]}'

        files = []
        for day, hw in sorted(
                tuple(data.items())[1:],
                key=lambda x: datetime.strptime(
                    f"{x[0].split()[0]} {months.index(x[0].split()[1]) + 1}", "%d %m")
        ):
            if string:
                string += '\n\n'
            string += f'<b>{day}</b>:\n\n'
            for lesson, homework in hw.items():
                file_string = ''
                homework = homework.split(', file=')
                if len(homework) == 2:
                    caption = f'{lesson} на {day}'
                    files.append((homework[1], caption))
                    file_string = f'\n\t<b>Файл</b> - {homework[1]}'
                string += f'- <b>{lesson}</b>: {homework[0]}{file_string}\n'

        await message.answer(string)

        for f, caption in files:
            await message.answer_document(FSInputFile(fr'{os.getcwd()}\files\{f}'), caption=caption)


@dp.message(Command('register'))
async def registration(message: Message, state: FSMContext):
    await message.answer("Введите свой логин mos.ru:")
    await state.set_state(RegisterStatesGroup.login)


@dp.message(StateFilter(RegisterStatesGroup.login))
async def handle_login(message: Message, state: FSMContext):
    await message.answer("Введите свой пароль:")
    await state.update_data(login=message.text)
    await state.set_state(RegisterStatesGroup.password)


@dp.message(StateFilter(RegisterStatesGroup.password))
async def handle_password(message: Message, state: FSMContext):

    await message.answer("Подождите минутку, проверяю по базе пользователей...")

    await state.update_data(password=message.text)
    uid = message.from_user.id

    data = await state.get_data()

    login = data['login']
    password = data['password']
    password_encrypt = cipher_suite.encrypt(password.encode())
    await state.clear()

    driver = create_driver(incognito=True)
    driver.get("https://school.mos.ru/")
    driver.set_window_size(1920, 1080)
    driver.set_window_position(0, 0)
    await asyncio.sleep(2)
    log_in = driver.find_element(By.XPATH, ".//div[contains(@class, 'style_btn__3lIWs')]")
    log_in.click()
    await asyncio.sleep(5)
    driver.find_element(By.ID, "login").send_keys(login)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "bind").click()
    await asyncio.sleep(30)
    if check_element_exists(driver, By.XPATH, ".//blockquote[contains(@class, 'blockquote-danger')]"):
        await message.answer("Неверный логин или пароль, попробуйте еще раз\n\n"
                             "Введите свой логин mos.ru:")
        await state.set_state(RegisterStatesGroup.login)
    else:
        await message.answer("Регистрация успешна! Теперь вы можете пользоваться командами, требующими вход в МЭШ")

        connection = sqlite3.connect("school.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Users SET (login, password) = (?,?) WHERE id = ?", (login, password_encrypt, uid))
        connection.commit()
        connection.close()
    driver.quit()


@dp.message(Command('gd'))
async def get_data(message: Message):
    connection = sqlite3.connect("school.db")
    cursor = connection.cursor()

    users = cursor.execute("SELECT * FROM Users").fetchall()

    for user in users:
        print(user)

    connection.commit()
    connection.close()


@dp.message(Command('files_blacklist'))
async def files_blacklist(message: Message, state: FSMContext):

    """
    Добавить предмет в черный список, чтобы файлы в нем не искались
    Это поможет быстрее загружать домашку
    """

    await message.answer("Введите название предмета, к которому никогда не прикрепляют файлы:\n\n"
                         "(Если таких несколько, напишите каждый с новой строки)")
    await state.set_state(BlacklistStatesGroup.subject)


@dp.message(StateFilter(BlacklistStatesGroup.subject))
async def handle_subject(message: Message, state: FSMContext):

    await state.clear()
    subjects = message.text

    with open("blacklist.txt", "a", encoding='utf-8') as f:
        f.write(subjects)

    await message.answer(f"<b>Предметы добавлены в черный список:</b>\n\n{subjects}")


def register_handlers_account():
    dp.message.register(schedule_command, Command('schedule'))
    dp.message.register(next_lesson_command, Command('next_lesson'))
    dp.message.register(load_hw_command, Command('load_homework'))
    dp.message.register(homework_command, Command('homework'))
    dp.message.register(registration, Command('register'))
    dp.message.register(get_data, Command('gd'))
    dp.message.register(files_blacklist, Command('files_blacklist'))
