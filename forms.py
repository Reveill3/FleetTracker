from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField, IntegerField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo, NumberRange)
from wtforms import ValidationError
from models import User, treaters
from flask_login import current_user

crews = [('yard', 'Yard'), ('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('onyx', 'Onyx'),
         ('gold', 'Gold')]


maintenance_types = [('select maintenance', 'Select Maintenance'),
                     ('valves & seats', 'Valves & Seats'), ('packing', 'Packing'), ('other', 'Other')]

holes = [('select hole', 'Select Hole'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]

numbers = [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
           ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')]

treater_list = list(map(lambda x: x['fields']['Name'], treaters.get_all()))

treater_choices = list(map(lambda x: (x, x), treater_list))


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


def equipment_exists(form, field):
    if Equipment.select().where(Equipment.unitnumber == field.data).exists():
        raise ValidationError('Equipment with that unit number already exists.')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

    crew = SelectField(
        'Crew',
        choices=crews
    )


class LoginForm(FlaskForm):
    username = StringField(
        'username',
        validators=[
            DataRequired()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ])


class AddForm(FlaskForm):
    unitnumber = StringField(
        'unitnumber',
        validators=[
            DataRequired(),
            Regexp(
                r'[0-9]{2}\w+-[0-9]{4,5}',
                message='input must be in this format: 53Q-11456'
            ), equipment_exists
        ]
    )

    type = SelectField('type',
                       choices=[('pump', 'Pump'), ('blender', 'Blender'), ('float', 'Float'),
                                ('hydration', 'Hydration'), ('missile', 'Missile')]
                       )

    crew = SelectField('crew',
                       choices=crews
                      )


class SearchForm(FlaskForm):
    search = StringField('search',
                         validators=[
                            DataRequired(),
                            Regexp(
                             r'[0-9]{2}\w+-[0-9]{4,5}',
                             message='input must be in this format: 53Q-11456'
                            )
                         ]
                         )


class PumpForm(FlaskForm):

    pumps = RadioField('pumps')

    pumps_crew = SelectField(
        'Crew',
        choices=crews
    )


class BlenderForm(FlaskForm):

    blenders = RadioField('blenders')

    blenders_crew = SelectField(
        'Crew',
        choices=crews
    )


class HydrationForm(FlaskForm):

    hydrations = RadioField('blenders')

    hydrations_crew = SelectField(
        'Crew',
        choices=crews
    )


class FloatForm(FlaskForm):

    floats = RadioField('floats')

    floats_crew = SelectField(
        'Crew',
        choices=crews
    )

class MissileForm(FlaskForm):

    missiles = RadioField('missiles')

    missiles_crew = SelectField(
        'Crew',
        choices=crews
    )

class AdminForm(FlaskForm):

    crew = SelectField('crew',
                       choices=crews
                       )


class MaintenanceForm(FlaskForm):

    maintenance_type = SelectField('maintenance_type',
                                   choices=maintenance_types
                                   )



class HoleForm(FlaskForm):
    Hole = SelectField('Hole',
                       choices=holes
                       )


class PartsFormVS(FlaskForm):

    suction_valves = SelectField(
        'Suction-Valves',
        choices=numbers
    )

    suction_seats = SelectField(
        'Suction-Seats',
        choices=numbers
    )

    discharge_valves = SelectField(
        'Discharge-Valves',
        choices=numbers
    )

    discharge_seats = SelectField(
        'Discharge-Seats',
        choices=numbers
    )


class PartsFormPacking(FlaskForm):

    four_point_five_packing = SelectField(
        '4.5 Inch Packing',
        choices=numbers
    )

    five_packing = SelectField(
        'Five Inch Packing',
        choices=numbers
    )


class GreaseForm(FlaskForm):

    grease_psi = IntegerField(
        'Grease Pressure',
        validators=[NumberRange(min=0, max=10000, message='Grease Pressure must be a number less than 10000'),
                    DataRequired(),
                    ]
    )

    treater_name = SelectField(
        'Treater Name',
        choices=treater_choices
    )
