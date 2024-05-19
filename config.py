import os
from dotenv import load_dotenv, find_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")

DEFAULT_COMMANDS = (
    ("about", "Информация о боте 🤖"),
    ("edit", "Изменить информацию о себе ⚙️")
)


def positions_list():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Директор", callback_data="Директор"),
        InlineKeyboardButton("РОП", callback_data="РОП"),
        InlineKeyboardButton("РОМ", callback_data="РОМ"),
        InlineKeyboardButton("Бухгалтер", callback_data="Бухгалтер"),
        InlineKeyboardButton("Клинер", callback_data="Клинер"),
        InlineKeyboardButton("Шеф", callback_data="Шеф"),
        InlineKeyboardButton("Повар", callback_data="Повар"),
        InlineKeyboardButton("Помощник повара", callback_data="Помощник повара"),
    )
    return markup


def start_work_action():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Начать работу 👏", callback_data="work_start")
    )
    return markup


def end_work_action():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Закончить работу 🏁", callback_data="work_end")
    )
    return markup


def end_work():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Начинаю работу", callback_data="work_start"),
        InlineKeyboardButton("Заканчиваю работу", callback_data="work_end")
    )
    return markup
