import datetime
from airtable import Airtable
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

DATABASE = SqliteDatabase('Fleet.db')

equipment = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Equipment', api_key='keyVE2OTPcmyTURGm')
movement = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Movement', api_key='keyVE2OTPcmyTURGm')
users = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Users', api_key='keyVE2OTPcmyTURGm')
maintenance = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Maintenance', api_key='keyVE2OTPcmyTURGm')

def check_crew(crew, unit_number):
    """ Checks to see if the current piece of equipment selected is
    already on the selected crew you want to move it to"""
    query = equipment.search('UnitNumber', unit_number)
    print(query)
    return query[0]['fields']['Crew'] == crew


def create_list(crew, equipment_type):
    """ Populates list of unit numbers for users crew or admins selected crew. This is used to populate form choices """
    color_filter = equipment.search('Crew', crew)
    equipment_filter = list(filter(lambda e: e['fields']['Type'] == equipment_type, color_filter))

    equipment_list = []
    for unit in equipment_filter:
        equipment_list.append((unit['fields']['UnitNumber'], unit['fields']['UnitNumber']))
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
    unitnumber = CharField(unique=True, primary_key=True)
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
    user = TextField()
    message = TextField()
    inTransit = BooleanField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    unit_number = CharField()
    crew_transfer = CharField()
    crew_from = CharField()
    details = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


class Maintenance(Model):
    user = TextField()
    maintenance_type = TextField()
    hole = IntegerField()
    equipment = ForeignKeyField(Equipment, related_name='maintenance')
    timestamp = DateTimeField(default=datetime.datetime.now)
    suction_valves = IntegerField()
    suction_seats = IntegerField()
    discharge_valves = IntegerField()
    discharge_seats = IntegerField()
    five_packing = IntegerField()
    four_point_five_packing = IntegerField()
    grease_pressure = IntegerField()

    @classmethod
    def add_maintenance(cls, maintenance_type, hole, equipment,
                        suction_valves, suction_seats, discharge_valves, discharge_seats,
                        five_packing, four_point_five_packing, grease_pressure, user):
        with DATABASE.transaction():
            cls.create(equipment=equipment, hole=hole, maintenance_type=maintenance_type,
                       suction_seats=suction_seats,suction_valves=suction_valves, discharge_valves=discharge_valves,
                       discharge_seats=discharge_seats,
                       five_packing=five_packing, four_point_five_packing=four_point_five_packing,
                       grease_pressure=grease_pressure, user=user)

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Equipment, Movement, Maintenance], safe=True)
    DATABASE.close()

def initialize_csv():
    df = pd.read_csv('initialize.csv')
    df.columns = df.columns.str.strip()
    num_rows = len(df)
    con = create_engine('sqlite:///Fleet.db')
    for i in range(num_rows):
        try:
            df.iloc[i:i+1].to_sql(name="equipment",con=con, if_exists = 'append', index='unitnumber')
        except ValueError:
            print(df.iloc[i])
            pass
