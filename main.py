import telebot
from telebot.types import BotCommand, Message
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from peewee import IntegrityError
from models import User, create_models
from config import BOT_TOKEN, DEFAULT_COMMANDS, positions_list, start_work_action, end_work_action, GOOGLE_SHEET_ID, CREDENTIALS_FILE
from states import States
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)


scope = ['https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive.readonly',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/spreadsheets.readonly']
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
worksheet = spreadsheet.sheet1


@bot.message_handler(state=States.start_work, commands=['start'])
def start(message: Message) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    name = user.name

    bot.send_message(message.chat.id,
                     f'Приветствую, {name}!\n\nРад снова Вас видеть 👋🏻'.format(name=name),
                     reply_markup=end_work_action())


@bot.message_handler(state=States.end_work, commands=['start'])
def start(message: Message) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    name = user.name

    bot.send_message(message.chat.id,
                     f'Приветствую, {name}!\n\nРад снова Вас видеть 👋🏻'.format(name=name),
                     reply_markup=start_work_action())


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    user_id: int = message.from_user.id
    username: str = message.from_user.username

    try:
        User.create(
            user_id=user_id,
            username=username,
        )

        bot.send_message(
            message.chat.id,
            'Приветствую! Я веду учет рабочего времени ⏱️\n\nДля продолжения, введите свои данные '
            '\n\nВаше ФИО ⤵️'
        )

        bot.set_state(message.from_user.id, States.name, message.chat.id)
    except IntegrityError:
        user_id = message.from_user.id
        user = User.get_or_none(User.user_id == user_id)
        name = user.name

        if name is None:
            bot.send_message(message.chat.id, 'Напишите Ваше ФИО')
            bot.set_state(message.from_user.id, States.name, message.chat.id)
            return

        bot.send_message(message.chat.id,
                         f'Приветствую, {name}!\n\nРад снова Вас видеть 👋🏻'.format(name=name),
                         reply_markup=start_work_action())


@bot.message_handler(state=States.name)
def name(message: Message) -> None:

    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    user.name = message.text
    user.save()

    bot.send_message(
        message.chat.id, f'Очень приятно, {message.text}!\n\nТеперь выберите должность из списка ниже ⤵️'.format(
            name=message.text.title()), reply_markup=positions_list()
    )

    bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(callback_query):

    if callback_query.data == "work_start":
        bot.set_state(callback_query.from_user.id, States.start_work)
        start_work(callback_query.message)
    elif callback_query.data == "work_end":
        bot.set_state(callback_query.from_user.id, States.end_work)
        end_work(callback_query.message)

    elif callback_query.data in [
        'Директор',
        'РОП',
        'РОМ',
        'Бухгалтер',
        'Клинер',
        'Шеф',
        'Повар',
        'Помощник повара',
    ]:
        user = User.get(User.user_id == callback_query.from_user.id)
        user.position = callback_query.data.title()
        user.save()
        bot.send_message(
            callback_query.message.chat.id, f'Ваша должность — {callback_query.data.title()}\n\nСпасибо, что заполнили данные 👍️', reply_markup=start_work_action()
        )


@bot.message_handler(commands=["edit"])
def edit_name(message: Message) -> None:
    bot.send_message(message.chat.id, f'Чтобы изменить данные, придется заново ввести их\n\nВведите ваши ФИО ⤵️')
    bot.set_state(message.from_user.id, States.name, message.chat.id)


def start_work(message: Message):
    user_id = message.chat.id
    user = User.get_or_none(User.user_id == user_id)

    name = user.name
    position = user.position
    start_time = datetime.now().strftime('%H:%M:%S')
    today_date = datetime.now().strftime('%Y-%m-%d')

    row = [user_id, today_date, name, position, start_time]
    worksheet.append_row(row)

    bot.send_message(message.chat.id,
                     f'Вы начали работу в {start_time}\n\nХорошего рабочего дня 🤗\n\n',
                     reply_markup=end_work_action())


def end_work(message: Message) -> None:
    user_id = message.chat.id
    end_time = datetime.now().strftime('%H:%M:%S')

    user_rows = worksheet.findall(str(user_id), in_column=1)
    last_row = user_rows[-1].row if user_rows else None

    if last_row:
        worksheet.update(range_name=f'F{last_row}', values=[[end_time]])

    bot.send_message(message.chat.id, f'Вы закончили работу в {end_time}\n\nДо свидания 🤗', reply_markup=start_work_action())
    bot.set_state(message.from_user.id, States.end_work, message.chat.id)


@bot.message_handler(state=States.start_work, commands=["about"])
def about(message: Message) -> None:
    bot.send_message(message.chat.id, f'Тут будет краткая информация о боте ...\n\nВыберите действие ⤵️', reply_markup=end_work_action())


@bot.message_handler(state=States.end_work, commands=["about"])
def about(message: Message) -> None:
    bot.send_message(message.chat.id, f'Тут будет краткая информация о боте ...\n\nВыберите действие ⤵️', reply_markup=start_work_action())


@bot.message_handler(commands=["about"])
def about(message: Message) -> None:
    bot.send_message(message.chat.id, f'Тут будет краткая информация о боте ...')


@bot.message_handler(commands=["info"])
def info(message: Message):
    user = User.get_or_none(message.from_user.id)
    msg = str(message.chat.id)

    state = bot.get_state(user, message.chat.id)
    bot.send_message(message.chat.id, state)


if __name__ == "__main__":
    create_models()
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
    bot.infinity_polling()
