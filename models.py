from peewee import (
    CharField,
    IntegerField,
    Model,
    SqliteDatabase
)

from config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """
    Базовый Класс
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс. Описывает пользователя. Наследуется от базового класса
    """
    user_id: int = IntegerField(primary_key=True)
    username: str = CharField()
    name: str = CharField(null=True)
    position: str = CharField(null=True)


def create_models() -> None:
    """
    Функция. Создает все модели. В данном случае создается только модель пользователя (User)
    :return: None
    """
    db.create_tables(BaseModel.__subclasses__())
