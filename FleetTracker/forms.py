from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)
from wtforms import ValidationError
from models import User, Equipment
from flask_login import current_user

crews = [('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('onyx', 'Onyx'),
         ('purple', 'Purple'), ('silver', 'Silver'), ('gold', 'Gold')]

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
                                ('hydration', 'Hydration')]
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


class AdminForm(FlaskForm):

    crew = SelectField('crew',
                       choices=crews
                       )
