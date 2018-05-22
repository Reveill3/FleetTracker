import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('Fleet.db')


def create_list(user, equipment_type):
    query = list(Equipment.select().where(Equipment.crew == user.crew,
                                          Equipment.type == equipment_type))
    equipment_list = []
    for equipment in query:
        equipment_list.append((equipment.unitnumber, equipment.unitnumber))
    return equipment_list


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    crew = CharField()

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, email, password, crew, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin,
                    crew=crew
                )
        except IntegrityError:
            raise ValueError("User already exists")


class Equipment(Model):
    unitnumber = CharField(unique=True)
    type = CharField()
    crew = CharField()

    @classmethod
    def add_equipment(cls, unitnumber, etype, crew):
        try:
            with DATABASE.transaction():
                cls.create(
                    unitnumber=unitnumber,
                    type=etype,
                    crew=crew,
                )
        except IntegrityError:
            raise IntegrityError('That Equipment already exists')

    class Meta:
        database = DATABASE


class Movement(Model):
    user = ForeignKeyField(User, related_name='movement')
    message = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Equipment, Movement], safe=True)
    DATABASE.close()
