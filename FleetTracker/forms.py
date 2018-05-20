from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)
from wtforms import ValidationError
from models import User, Equipment


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


def equipment_exists(form, field):
    if Equipment.select().where(Equipment.unitnumber == field.data).exists():
        raise ValidationError('Equipment with that unit number already exists.')


class RegisterForm(Form):
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
        choices=[('red', 'Red'), ('blue', 'Blue')]
    )


class LoginForm(Form):
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


class AddForm(Form):
    unitnumber = StringField(
        'unitnumber',
        validators=[
            DataRequired(),
            Regexp(
                r'[0-9]{2}\w-[0-9]{5}',
                message='input must be in this format: 53Q-11456'
            ), equipment_exists
        ]
    )

    type = SelectField('type',
                       choices=[('pump', 'Pump'), ('blender', 'Blender')]
                       )

    crew = SelectField('crew',
                       choices=[('red', 'Red'), ('blue', 'Blue')]
                      )




