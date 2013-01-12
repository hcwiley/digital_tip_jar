import config
from flask import request, render_template, redirect, url_for, flash
from digitial_tip_jar import app
from utils import slugify
from user import *

@app.route('/', methods=['POST','GET'])
def index():
    users = get_users()
    return render_template('index.html', users=users)


@app.route('/<user_name>')
def job(user_name):
    user = get_user(user_name)
    if user is not None:
        return render_template('band_page.html', user=user)

    return "Error"

def validate_user(user_form):
    if len(user_form['first_name']) == 0:
        return "First Name is required"

    if len(user_form['last_name']) == 0:
        return "Last Name is required"


@app.route('/register', methods=['GET', 'POST'])
@app.route('/update/<user_name>', methods=['GET', 'POST'])
def edit(user_name = None):

    if request.method == 'POST':

        message = validate_user(request.form)

        if message is None:
            if user_name is None:
                slug = slugify(request.form['first_name'] + request.form['last_name'],get_users())
                flash('Registered Successfully',category='success')
            else:
                flash('Updated Successfully',category='success')
                slug = user_name

            save_user(User(request.form['first_name'], request.form['last_name'], slug, request.form['band_name']))

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



