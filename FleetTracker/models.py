import datetime
from airtable import Airtable
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import uuid

DATABASE = SqliteDatabase('Fleet.db')

equipment = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Equipment', api_key='keyVE2OTPcmyTURGm')
movement = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Movement', api_key='keyVE2OTPcmyTURGm')
users = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Users', api_key='keyVE2OTPcmyTURGm')
maintenance = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Maintenance', api_key='keyVE2OTPcmyTURGm')
treaters = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Treaters', api_key='keyVE2OTPcmyTURGm')

def add_user(username, crew, password, is_admin=False):
    users.insert({'id': uuid.uuid4().hex,'UserName': username, 'Crew': crew,
    'Password': generate_password_hash(password).decode("utf-8"), 'is_admin': is_admin}, typecast=True)

def check_crew(crew, unit_number):
    """ Checks to see if the current piece of equipment selected is
    already on the selected crew you want to move it to"""
    query = equipment.search('UnitNumber', unit_number)
    return query[0]['fields']['Crew'] == crew


def create_list(crew, equipment_type):
    """ Populates list of unit numbers for users crew or admins selected crew. This is used to populate form choices """
    color_filter = equipment.search('Crew', crew)
    equipment_filter = list(filter(lambda e: e['fields']['Type'] == equipment_type, color_filter))

    equipment_list = []
    for unit in equipment_filter:
        equipment_list.append((unit['fields']['UnitNumber'], unit['fields']['UnitNumber']))
    return equipment_list

class User(UserMixin):
    def __init__(self, id, username, password, crew):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = False
        self.crew = crew
