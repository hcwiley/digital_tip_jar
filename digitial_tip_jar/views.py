import config
from flask import request, render_template, redirect, url_for, flash, session
from digitial_tip_jar import app
from utils import qrcode_string, is_username_unique
from user import *

@app.route('/')
def index():
    users = get_users()
    return render_template('index.html', users=users)


def validate_login(user_name, password):
    if len(user_name) == 0:
        return "Username not specified"

    if len(password) == 0:
        return "Password not specified"

    if get_user(user_name) is None or get_user(user_name).check_password(password) is False:
        return "Invalid Username or Password"

    return None

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        message = validate_login(user_name, password)

        if message:
            flash(message,category='error')
            render_template('login.html')
        else:
            session['user_name'] = user_name
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('index'))


@app.route('/<user_name>')
def job(user_name):
    user = get_user(user_name)
    if user is not None:
        return render_template('band_page.html', user=user)

    return "Error"

def validate_new_user(user_form):
    if len(user_form['band_name']) == 0:
        return "Artist/Band Name is required"

    if len(user_form['user_name']) == 0:
        return "Username is required"

    if is_username_unique(user_form['user_name'], get_users()) is False:
        return "Username already taken"

    if len(user_form['email']) == 0:
        return "Email is required"

    if len(user_form['password']) == 0:
        return "Password is required"

def validate_update_user(user_form):
    if len(user_form['band_name']) == 0:
        return "Artist/Band Name is required"

    if len(user_form['user_name']) == 0:
        return "Username is required"

    if len(user_form['email']) == 0:
        return "Email is required"


@app.route('/register', methods=['GET', 'POST'])
@app.route('/update/<user_name>', methods=['GET', 'POST'])
def edit(user_name = None):

    if request.method == 'POST':

        if user_name:
            message = validate_update_user(request.form)
        else:
            message = validate_new_user(request.form)

        if message is None:
            # [XXX] Hardcoded shit
            qr_path = qrcode_string("http://75.126.35.122/"+user_name)

            if user_name is None:
                user = User(request.form['user_name'], request.form['band_name'], request.form['email'], qr_path, request.form['password'])
                flash('Registered Successfully',category='success')
            else:
                user = get_user(user_name)
                user.band_name = request.form['band_name']
                user.email = request.form['email']

                if 'password' in request.form and len(request.form['password']) > 0:
                    user.set_password(request.form['password'])

                flash('Updated Successfully',category='success')


            save_user(user)

            return redirect(url_for('index'))
        else:
            flash(message,category='error')
            return render_template('register.html', user=None)


    else:
        if user_name:
            user = get_user(user_name)
            return render_template('register.html', user=user)
        else:
            return render_template('register.html', user=None)



