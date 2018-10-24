from flask import (Flask, g, render_template, flash, redirect, url_for,
                   make_response, request)
import json
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from resources.transit import transit_api
from resources.get_equipment_list import get_api
from resources.get_treaters import get_treaters
from resources.move_equipment import move_equipment
from resources.log_maintenance import log_maintenance
from resources.update_layout import update_layout
from resources.update_pump_hours import update_pump_hours
from resources.delete_note import delete_note
from resources.add_note import add_note
from flask_cors import CORS, cross_origin

import forms
import models
import os
import re
import uuid
from datetime import datetime


THREADED = True
DEBUG = True
PORT = 8000
HOST = '192.168.86.26'

app = Flask(__name__)
app.register_blueprint(transit_api)
app.register_blueprint(get_api)
app.register_blueprint(get_treaters)
app.register_blueprint(move_equipment)
app.register_blueprint(log_maintenance)
app.register_blueprint(update_layout)
app.register_blueprint(update_pump_hours)
app.register_blueprint(add_note)
app.register_blueprint(delete_note)
CORS(app)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.context_processor
def hash_processor():
    """Converts hashed JS files from Webpack build step back to normal"""
    def hashed_url(filepath):
        directory, filename = filepath.rsplit('/')
        name, extension = filename.rsplit(".")
        folder = os.path.join(app.root_path, 'static', directory)
        files = os.listdir(folder)
        for f in files:
            regex = name+"\.[a-z0-9]+\."+extension
            if re.match(regex, f):
                return os.path.join('/static', directory, f)
        return os.path.join('/static', filepath)
    return dict(hashed_url=hashed_url)


def search_field(field, data, table):
    return table.search(field, data)[0]['fields']


def get_saved_data():
    try:
        data = json.loads(request.cookies.get('user_input'))
    except TypeError:
        data = {}
    return data


def convertTime(time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central


def move(equipment_field, crew_field, supervisor, message):
    """Moves a piece of equipment to specified crew in database.
    Changes 'crew' column in database to specified field"""
    models.equipment.update_by_field('UnitNumber', equipment_field.data, {'Crew': 'pending'})
    flash('{} moved to {} crew'.format(equipment_field.data, crew_field.data))
    models.movement.insert({'Movement_Id': uuid.uuid4().hex, 'User': supervisor, 'message': '{} has moved {} to {} crew'.format(
        supervisor, equipment_field.data, crew_field.data), 'inTransit': 'checked', 'UnitNumber': equipment_field.data,
        'CrewTransfer': crew_field.data, 'CrewFrom': current_user.crew, 'details': message, 'Treaters': supervisor}, typecast=True)


@login_manager.user_loader
def load_user(userid):
    user_data = search_field('id', userid, models.users)
    user = models.User(user_data['id'], user_data['UserName'],
                       str.encode(user_data['Password']), user_data['Crew'])
    return user


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    return response

@app.route('/')
def home():
    search_form = forms.SearchForm()
    return render_template('home.html', search_form=search_form)

@login_required
@app.route('/main')
def main():
    search_form = forms.SearchForm()
    return render_template('index.html', search_form=search_form, crew=current_user.crew)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    search_form = forms.SearchForm()
    if form.validate_on_submit():
        try:
            user_data = search_field('UserName', form.username.data, models.users)
            user = models.User(user_data['id'], user_data['UserName'],
                               str.encode(user_data['Password']), user_data['Crew'])
        except models.DoesNotExist:
            flash('Your username or password does not match', 'error')
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("You've been logged in.", 'success')
            if current_user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('main'))
        else:
            flash('Your username or password is incorrect', 'error')
        redirect(url_for('login'))
    return render_template('login.html', form=form, search_form=search_form, authedUser=current_user)

@app.route('/search', methods=["GET", "POST"])
def search():
    """Action for clicking search button in top right. Looks for crew of a piece of equipment and flashes to page. """
    search_form = forms.SearchForm()
    if current_user.is_admin:
        response = make_response(redirect(url_for('admin')))
    else:
        response = make_response(redirect(url_for('main')))
    if search_form.validate_on_submit():
        try:
            query = models.equipment.search('UnitNumber', search_form.search.data)
            flash('{} is on {} crew'.format(search_form.search.data, models.crews.get(query[0]['fields']['Crew'][0])['fields']['Name']))
        except:
            flash('{} is not in the system. If this is a mistake please inform admin.'.format(
                search_form.search.data))
        return response
    else:
        return response


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

if __name__ == '__main__':
#     # models.initialize()
#     # models.initialize_csv()
#     # try:
#     #     models.User.create_user(
#     #         username='alester',
#     #         email='austin.lester@ftsi.com',
#     #         password='password',
#     #         admin=True,
#     #         crew='red'
#     #     )
#     # except ValueError:
#     #     pass
    app.run(threaded=THREADED, debug=DEBUG, host=HOST, port=PORT)
