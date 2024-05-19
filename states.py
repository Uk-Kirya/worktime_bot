from telebot.handler_backends import State, StatesGroup


class States(StatesGroup):
    """
    Состояния.
    1 — Ввод ФИО и выбор должности
    2 — Начало рабочего дня
    3 — Конец рабочего дня
    """

    name = State()
    start_work = State()
    end_work = State()
