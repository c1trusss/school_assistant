import json
from dataclasses import dataclass
import sqlite3
import os

from aiogram.fsm.state import StatesGroup, State

from fake_useragent import UserAgent
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class Product:
    name: str
    kcal: int
    proteins: int
    fats: int
    carbohydrates: int
    composition: str


class User:

    def __init__(self, user_id=0):

        self.id = user_id

        if self.id:
            connection = sqlite3.connect("school.db")
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE id=?", (self.id,))

            user_data = cursor.fetchone()
            self.login = user_data[2]
            self.password_hash = user_data[3]
            self.username = user_data[1]
            self.created = user_data[4]
            self.admin = user_data[5]


class Action:

    def __init__(self, name):
        with open('actions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        if name not in data.keys():
            raise ValueError('Активность не найдена в базе данных')

        self.name = name
        self.date = data[name]["date"]
        self.description = data[name]["description"]
        self.contact = data[name]["contact"]
        self.status = data[name]["status"]
        self.creator = data[name]["creator"]
        self.votes_favor = data[name]["votes_favor"]
        self.votes_against = data[name]["votes_against"]


class DateError(Exception):
    pass


class BlacklistStatesGroup(StatesGroup):
    subject = State()


def create_driver(incognito=False):

    options = webdriver.ChromeOptions()
    if incognito:
        options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-cache")
    options.add_argument("--disable-application-cache")
    user_agent = UserAgent().random
    options.add_argument(f"--user-agent={user_agent}")
    prefs = {
        "download.default_directory": f"{os.getcwd()}\\files",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "plugins.always_open_pdf_externally": True,
        "download.extensions_to_open": ""
    }

    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=ChromeDriverManager().install())

    driver = webdriver.Chrome(options=options, service=service)
    driver.delete_all_cookies()
    driver.set_page_load_timeout(10000)
    return driver


def create_table_users():

    connection = sqlite3.connect("school.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    login TEXT,
    password TEXT
    )
    ''')

    connection.commit()
    connection.close()


def check_element_exists(driver, by, element) -> bool:
    try:
        driver.find_element(by, element)
    except NoSuchElementException:
        return False
    return True

