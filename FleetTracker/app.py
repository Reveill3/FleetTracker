from flask import (Flask, g, render_template, flash, redirect, url_for,
                   make_response, request)
import json
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from resources.transit import transit_api
from flask_cors import CORS, cross_origin

import forms
import models
import os
import re
import uuid
from datetime import datetime
from dateutil import tz


THREADED = True
DEBUG = True
PORT = 8000
HOST = '192.168.86.26'

app = Flask(__name__)
app.register_blueprint(transit_api)
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
    models.movement.insert({'Movement_Id': uuid.uuid4().hex,'User': supervisor, 'message': '{} has moved {} to {} crew'.format(
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
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/')
def home():
    search_form = forms.SearchForm()
    return render_template('index.html', search_form=search_form)


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('Registration Success!', "success")
        models.add_user(form.username.data, form.crew.data, form.password.data)
        return redirect(url_for('main'))
    return render_template('register.html', form=form)


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
        redirect(url_for('home'))
    return render_template('login.html', form=form, search_form=search_form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    """validate add equipment form. renders add equipment page with form."""
    form = forms.AddForm()
    search_form = forms.SearchForm()
    if form.validate_on_submit():
        models.Equipment.add_equipment(unitnumber=form.unitnumber.data, etype=form.type.data,
                                       crew=form.crew.data)
        flash('{} {} added.'.format(form.type.data, form.unitnumber.data))
        redirect('home')
    return render_template('add.html', form=form, user=current_user, search_form=search_form)


@app.route('/main', methods=('GET', 'POST'))
@app.route('/main/<crew>', methods=('GET', 'POST'))
@login_required
def main(crew=None):
    """Builds initial main template. Buttons go to different routes that perform actions and redirect back to here."""
    response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    movement_stream = models.movement.get_all(maxRecords=10, sort=[('timestamp', 'desc'),])
    if crew is not None and current_user.is_admin:
        pump_numbers = models.create_list(crew, 'pump')
        blender_numbers = models.create_list(crew, 'blender')
        hydration_numbers = models.create_list(crew, 'hydration')
        float_numbers = models.create_list(crew, 'float')
        missile_numbers = models.create_list(crew, 'missile')
    else:
        pump_numbers = models.create_list(current_user.crew, 'pump')
        blender_numbers = models.create_list(current_user.crew, 'blender')
        hydration_numbers = models.create_list(current_user.crew, 'hydration')
        float_numbers = models.create_list(current_user.crew, 'float')
        missile_numbers = models.create_list(current_user.crew, 'missile')
    pump_form = forms.PumpForm()
    search_form = forms.SearchForm()
    pump_form.pumps.choices = pump_numbers
    blender_form = forms.BlenderForm()
    blender_form.blenders.choices = blender_numbers
    float_form = forms.FloatForm()
    float_form.floats.choices = float_numbers
    hydration_form = forms.HydrationForm()
    hydration_form.hydrations.choices = hydration_numbers
    missile_form = forms.MissileForm()
    missile_form.missiles.choices = missile_numbers

    return render_template('main.html', saves=get_saved_data(), pump_form=pump_form, blender_form=blender_form,
                           search_form=search_form, float_form=float_form, hydration_form=hydration_form, missile_form=missile_form,
                           movement_stream=movement_stream, crew=crew)


@app.route('/save', methods=['POST'])
def save():
    response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    return response


@app.route('/move_pump', methods=['POST', 'GET'])
@app.route('/move_pump/<crew>', methods=('GET', 'POST'))
@login_required
def move_pump(crew=None):
    """Action route from button on main page. Initiates moving equipment to selected crew in dropdown."""
    if crew is not None and current_user.is_admin:
        pump_numbers = models.create_list(crew, 'pump')
        response = make_response(redirect(url_for('admin')))
    else:
        pump_numbers = models.create_list(current_user.crew, 'pump')
        response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    pump_form = forms.PumpForm()
    pump_form.pumps.choices = pump_numbers
    treater_name = request.form.get('user_name')
    movement_message = request.form.get('user_message')
    if pump_form.validate_on_submit():
        if request.form['button'] == 'maintenance':
            response = make_response(redirect(url_for('maintenance', pump=pump_form.pumps.data)))
            return response
        if current_user.is_admin:
            if models.check_crew(pump_form.pumps_crew.data, pump_form.pumps.data):
                flash('{} is already on {} crew.'.format(pump_form.pumps.data, pump_form.pumps_crew.data))
                return response
            else:
                move(pump_form.pumps, pump_form.pumps_crew, treater_name, movement_message)
                return response
        elif pump_form.pumps_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(pump_form.pumps.data, pump_form.pumps_crew.data))
            return response
        else:
            move(pump_form.pumps, pump_form.pumps_crew, treater_name, movement_message)
            return response
    else:
        response = redirect(url_for('main'))
        flash('Please Select a Pump')
        return response


@app.route('/move_blender', methods=['POST', 'GET'])
@app.route('/move_blender/<crew>', methods=['POST', 'GET'])
@login_required
def move_blender(crew=None):
    """Action route from button on main page. Initiates moving equipment to selected crew in dropdown."""
    if crew is not None and current_user.is_admin:
        blender_numbers = models.create_list(crew, 'blender')
        response = make_response(redirect(url_for('admin')))
    else:
        blender_numbers = models.create_list(current_user.crew, 'blender')
        response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    blender_form = forms.BlenderForm()
    blender_form.blenders.choices = blender_numbers
    treater_name = request.form.get('user_name')
    movement_message = request.form.get('user_message')
    if blender_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(blender_form.blenders_crew.data, blender_form.blenders.data):
                flash('{} is already on {} crew.'.format(blender_form.blenders.data, blender_form.blenders_crew.data))
                return response
            else:
                move(blender_form.blenders, blender_form.blenders_crew, treater_name, movement_message)
                return response

        elif blender_form.blenders_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(blender_form.blenders.data, blender_form.blenders_crew.data))
            return response
        else:
            move(blender_form.blenders, blender_form.blenders_crew, treater_name, movement_message)
            return response
    else:
        response = redirect(url_for('main'))
        return response

@app.route('/move_missile', methods=['POST', 'GET'])
@app.route('/move_missile/<crew>', methods=['POST', 'GET'])
@login_required
def move_missile(crew=None):
    """Action route from button on main page. Initiates moving equipment to selected crew in dropdown."""
    if crew is not None and current_user.is_admin:
        missile_numbers = models.create_list(crew, 'missile')
        response = make_response(redirect(url_for('admin')))
    else:
        missile_numbers = models.create_list(current_user.crew, 'missile')
        response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    missile_form = forms.MissileForm()
    missile_form.missiles.choices = missile_numbers
    treater_name = request.form.get('user_name')
    movement_message = request.form.get('user_message')
    if missile_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(missile_form.missiles_crew.data, missile_form.missiles.data):
                flash('{} is already on {} crew.'.format(missile_form.missiles.data, missile_form.missiles_crew.data))
                return response
            else:
                move(missile_form.missiles, missile_form.missiles_crew, treater_name, movement_message)
                return response

        elif missile_form.missiles_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(missile_form.missiles.data, missile_form.missiles_crew.data))
            return response
        else:
            move(missile_form.missiles, missile_form.missiles_crew, treater_name, movement_message)
            return response
    else:
        response = redirect(url_for('main'))
        return response


@app.route('/move_hydration', methods=['POST', 'GET'])
@app.route('/move_hydration/<crew>', methods=['POST', 'GET'])
@login_required
def move_hydration(crew=None):
    """Action route from button on main page. Initiates moving equipment to selected crew in dropdown."""
    if crew is not None and current_user.is_admin:
        hydration_numbers = models.create_list(crew, 'hydration')
        response = make_response(redirect(url_for('admin')))
    else:
        response = make_response(redirect(url_for('main')))
        hydration_numbers = models.create_list(current_user.crew, 'hydration')
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    hydration_form = forms.HydrationForm()
    hydration_form.hydrations.choices = hydration_numbers
    treater_name = request.form.get('user_name')
    movement_message = request.form.get('user_message')
    if hydration_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(hydration_form.hydrations_crew.data, hydration_form.hydrations.data):
                flash('{} is already on {} crew.'.format(hydration_form.hydrations.data,
                                                         hydration_form.hydrations_crew.data))
                return response
            else:
                move(hydration_form.hydrations, hydration_form.hydrations_crew, treater_name, movement_message)
                return response

        elif hydration_form.hydrations_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(hydration_form.hydrations.data,
                                                     hydration_form.hydrations_crew.data))
            return response
        else:
            move(hydration_form.hydrations, hydration_form.hydrations_crew, treater_name, movement_message)
            return response
    else:
        response = redirect(url_for('main'))
        return response


@app.route('/move_float', methods=['POST', 'GET'])
@app.route('/move_float/<crew>', methods=['POST', 'GET'])
@login_required
def move_float(crew=None):
    """Action route from button on main page. Initiates moving equipment to selected crew in dropdown."""
    if crew is not None and current_user.is_admin:
        float_numbers = models.create_list(crew, 'float')
        response = make_response(redirect(url_for('admin')))
    else:
        float_numbers = models.create_list(current_user.crew, 'float')
        response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    float_form = forms.FloatForm()
    float_form.floats.choices = float_numbers
    treater_name = request.form.get('user_name')
    movement_message = request.form.get('user_message')
    if float_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(float_form.floats_crew.data, float_form.floats.data):
                flash('{} is already on {} crew.'.format(float_form.floats.data,
                                                         float_form.floats_crew.data))
                return response
            else:
                move(float_form.floats, float_form.floats_crew, treater_name, movement_message)
                return response

        elif float_form.floats_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(float_form.floats.data,
                                                     float_form.floats_crew.data))
            return response
        else:
            move(float_form.floats, float_form.floats_crew, treater_name, movement_message)
            return response

    else:
        response = redirect(url_for('main'))
        return response


@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    search_form = forms.SearchForm()
    admin_form = forms.AdminForm()
    movement_stream = models.movement.get_all(maxRecords=10, sort=[('timestamp', 'desc'),])

    if admin_form.validate_on_submit():
        return redirect(url_for('main', crew=admin_form.crew.data))

    return render_template('admin.html', admin_form=admin_form, search_form=search_form,
                           movement_stream=movement_stream)


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
            flash('{} is on {} crew'.format(search_form.search.data, query[0]['fields']['Crew']))
        except:
            flash('{} is not in the system. If this is a mistake please inform admin.'.format(search_form.search.data))
        return response
    else:
        return response


@app.route('/maintenance', methods=['get', 'post'])
@app.route('/maintenance/<pump>', methods=['get', 'post'])
@login_required
def maintenance(pump=None):
    """Logs maintenance into database"""
    maintenance_form = forms.MaintenanceForm()
    hole_form = forms.HoleForm()
    search_form = forms.SearchForm()
    parts_form_vs = forms.PartsFormVS()
    parts_form_packing = forms.PartsFormPacking()
    grease_form = forms.GreaseForm()
    maintenance_stream = models.maintenance.search('UnitNumber', pump, sort=[('Timestamp', 'desc'),])
    messages = []
    for maint_log in maintenance_stream:
        message = '{} did {} on {} Hole {} on {}'.format(models.treaters.get(maint_log['fields']['Treaters'][0])['fields']['Name'], maint_log['fields']['MaintenanceType'],
                                                               models.equipment.get(maint_log['fields']['UnitNumber'][0])['fields']['UnitNumber'], maint_log['fields']['Hole'],
                                                               convertTime(maint_log['fields']['Timestamp']))

        messages.append(message)

    if grease_form.validate_on_submit():
        try:
            models.maintenance.insert({'Id': uuid.uuid4().hex,'MaintenanceType': maintenance_form.maintenance_type.data, 'Hole': hole_form.Hole.data,
                                               'UnitNumber': [models.equipment.search('UnitNumber', pump)[0]['id']], 'suction_valves': int(parts_form_vs.suction_valves.data), 'suction_seats': int(parts_form_vs.suction_seats.data),
                                               'discharge_valves': int(parts_form_vs.discharge_valves.data), 'discharge_seats': int(parts_form_vs.discharge_seats.data),
                                               'five_packing': int(parts_form_packing.five_packing.data),
                                               'four_point_five_packing': int(parts_form_packing.four_point_five_packing.data), 'grease_pressure': int(grease_form.grease_psi.data),
                                               'Treaters': [models.treaters.search('Name', grease_form.treater_name.data)[0]['id']],
                                               'Crew': current_user.crew})
            flash('Maintenance logged for {}'.format(pump))
        except IndexError:
           flash('{} is not an authorized name. Contact admin for help.'.format(grease_form.treater_name.data))

        return redirect(url_for('maintenance', pump=pump))

    return render_template('maintenance.html', maintenance_form=maintenance_form,
                           hole_form=hole_form, search_form=search_form, parts_form_vs=parts_form_vs,
                           parts_form_packing=parts_form_packing, grease_form=grease_form, pump=pump,
                           maintenance_stream=messages)


if __name__ == '__main__':
    # models.initialize()
    # models.initialize_csv()
    # try:
    #     models.User.create_user(
    #         username='alester',
    #         email='austin.lester@ftsi.com',
    #         password='password',
    #         admin=True,
    #         crew='red'
    #     )
    # except ValueError:
    #     pass
    app.run(threaded=THREADED, debug=DEBUG, host=HOST, port=PORT)
