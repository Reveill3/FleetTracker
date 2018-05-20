from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)

from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8080
HOST = '10.209.139.170'

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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
        return redirect(url_for('index'))
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
            return redirect(url_for('home'))
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
        models.Equipment.add_equipment(unitnumber=form.unitnumber.data, etype=form.type.data, crew=form.crew.data)
        flash('{} {} added.'.format(form.type.data, form.unitnumber.data))
        redirect('home')
    return render_template('add.html', form=form)


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


