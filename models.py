import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = PostgresqlDatabase(
    'd6dtgpvg8ivgof',
    user='yzpybctnlcwbum',
    password='56a30895a701d58c57572c1e74ed59cc08066ccffe3ebe67563c46e3c6745a2e',
    host='ec2-54-163-246-5.compute-1.amazonaws.com',
    port=5432
)


def check_crew(crew, unit_number):
    """ Checks to see if the current piece of equipment selected is
    already on the selected crew you want to move it to"""
    query = Equipment.select().where(Equipment.unitnumber == unit_number).get()
    return query.crew == crew


def create_list(crew, equipment_type):
    """ Populates list of unit numbers for users crew or admins selected crew. This is used to populate form choices """
    query = list(Equipment.select().where(Equipment.crew == crew,
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
                       suction_seats=suction_seats, suction_valves=suction_valves, discharge_valves=discharge_valves,
                       discharge_seats=discharge_seats,
                       five_packing=five_packing, four_point_five_packing=four_point_five_packing,
                       grease_pressure=grease_pressure, user=user)

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Equipment, Movement, Maintenance], safe=True)
    DATABASE.close()
