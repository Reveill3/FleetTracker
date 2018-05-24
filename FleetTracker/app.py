from flask import (Flask, g, render_template, flash, redirect, url_for,
                   make_response, request)
import json
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8080
HOST = '10.105.160.35'

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def get_saved_data():
    try:
        data = json.loads(request.cookies.get('user_input'))
    except TypeError:
        data = {}
    return data


def move(equipment_field, crew_field):
    models.Equipment.update(crew=crew_field.data).where(
        models.Equipment.unitnumber ==
        equipment_field.data).execute()
    flash('{} moved to {} crew'.format(equipment_field.data, crew_field.data))
    models.Movement.create(user=g.user.id, message='{} has moved {} to {} crew'.format(
        current_user.username, equipment_field.data, crew_field.data))


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


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
    return render_template('index.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('Registration Success!', "success")
        models.User.create_user(username=form.username.data, email=form.email.data, password=form.password.data
                                , crew=form.crew.data)
        return redirect(url_for('main'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
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
    return render_template('login.html', form=form)


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
    if form.validate_on_submit():
        models.Equipment.add_equipment(unitnumber=form.unitnumber.data, etype=form.type.data,
                                       crew=form.crew.data)
        flash('{} {} added.'.format(form.type.data, form.unitnumber.data))
        redirect('home')
    return render_template('add.html', form=form, user=current_user)


@app.route('/main', methods=('GET', 'POST'))
@app.route('/main/<crew>', methods=('GET', 'POST'))
@login_required
def main(crew=None):
    response = make_response(redirect(url_for('main')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('user_input', json.dumps(data))
    movement_stream = models.Movement.select().order_by(models.Movement.timestamp.desc()).limit(10)
    if crew is not None and current_user.is_admin:
        pump_numbers = models.create_list(crew, 'pump')
        blender_numbers = models.create_list(crew, 'blender')
        hydration_numbers = models.create_list(crew, 'hydration')
        float_numbers = models.create_list(crew, 'float')
    else:
        pump_numbers = models.create_list(current_user.crew, 'pump')
        blender_numbers = models.create_list(current_user.crew, 'blender')
        hydration_numbers = models.create_list(current_user.crew, 'hydration')
        float_numbers = models.create_list(current_user.crew, 'float')
    pump_form = forms.PumpForm()
    pump_form.pumps.choices = pump_numbers
    blender_form = forms.BlenderForm()
    blender_form.blenders.choices = blender_numbers
    float_form = forms.FloatForm()
    float_form.floats.choices = float_numbers
    hydration_form = forms.HydrationForm()
    hydration_form.hydrations.choices = hydration_numbers

    return render_template('main.html', saves=get_saved_data(), pump_form=pump_form, blender_form=blender_form,
                           float_form=float_form, hydration_form=hydration_form,
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

    if pump_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(pump_form.pumps_crew, pump_form.pumps.data):
                flash('{} is already on {} crew.'.format(pump_form.pumps.data, pump_form.pumps_crew.data))
                return response
            else:
                move(pump_form.pumps, pump_form.pumps_crew)
                return response
        elif pump_form.pumps_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(pump_form.pumps.data, pump_form.pumps_crew.data))
            return response
        else:
            move(pump_form.pumps, pump_form.pumps_crew)
            return response


@app.route('/move_blender', methods=['POST', 'GET'])
@app.route('/move_blender/<crew>', methods=['POST', 'GET'])
@login_required
def move_blender(crew=None):
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

    if blender_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(blender_form.blenders_crew, blender_form.blenders.data):
                flash('{} is already on {} crew.'.format(blender_form.blenders.data, blender_form.blenders_crew.data))
                return response
            else:
                move(blender_form.blenders, blender_form.blenders_crew)
                return response

        elif blender_form.blenders_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(blender_form.blenders.data, blender_form.blenders_crew.data))
            return response
        else:
            move(blender_form.blenders, blender_form.blenders_crew)
            return response


@app.route('/move_hydration', methods=['POST', 'GET'])
@app.route('/move_hydration/<crew>', methods=['POST', 'GET'])
@login_required
def move_hydration(crew=None):
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

    if hydration_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(hydration_form.hydrations_crew, hydration_form.hydrations.data):
                flash('{} is already on {} crew.'.format(hydration_form.hydrations.data,
                                                         hydration_form.hydrations_crew.data))
                return response
            else:
                move(hydration_form.hydrations, hydration_form.hydrations_crew)
                return response

        elif hydration_form.hydrations_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(hydration_form.hydrations.data,
                                                     hydration_form.hydrations_crew.data))
            return response
        else:
            move(hydration_form.hydrations, hydration_form.hydrations_crew)
            return response


@app.route('/move_float', methods=['POST', 'GET'])
@app.route('/move_float/<crew>', methods=['POST', 'GET'])
@login_required
def move_float(crew=None):
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

    if float_form.validate_on_submit():
        if current_user.is_admin:
            if models.check_crew(float_form.floats_crew, float_form.floats.data):
                flash('{} is already on {} crew.'.format(float_form.floats.data,
                                                         float_form.floats_crew.data))
                return response
            else:
                move(float_form.floats, float_form.floats_crew)
                return response

        elif float_form.floats_crew.data == current_user.crew:
            flash('{} is already on {} crew.'.format(float_form.floats.data,
                                                     float_form.floats_crew.data))
            return response
        else:
            move(float_form.floats, float_form.floats_crew)
            return response


@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    admin_form = forms.AdminForm()
    movement_stream = models.Movement.select().order_by(models.Movement.timestamp.desc()).limit(10)

    if admin_form.validate_on_submit():
        return redirect(url_for('main', crew=admin_form.crew.data))

    return render_template('admin.html', admin_form=admin_form, movement_stream=movement_stream)


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='alester',
            email='austin.lester@ftsi.com',
            password='password',
            admin=True,
            crew='red'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)


