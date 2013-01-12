import config
from flask import request, render_template, redirect, url_for, flash, session, jsonify
from digitial_tip_jar import app
from utils import qrcode_string, is_username_unique
from artist import *
from flask_oauth import OAuth
import json
import datetime
from tip import *

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.FACEBOOK_APP_ID,
    consumer_secret=config.FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    artists = get_artists()
    return render_template('index.html', artists=artists)


def validate_login(user_name, password):
    if len(user_name) == 0:
        return "Username not specified"

    if len(password) == 0:
        return "Password not specified"

    if get_artist(user_name) is None or get_artist(user_name).check_password(password) is False:
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
            session['logged_in'] = True
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    session.pop('logged_in', None)
    return redirect(url_for('index'))
 
@app.route('/fblogin')
def fblogin():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/fblogin/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['artists']
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    session['logged_in'] = True
# This is what me.data contains:
# {"username": "epsasnova", "first_name": "Chrrles", "last_name": "Paul", "verified": true, "name": "Chrrles Paul", "locale": "en_US", "gender": "male", "email": "vmproperly@gmail.com", "link": "http://www.facebook.com/epsasnova", "timezone": -6, "updated_time": "2012-12-07T12:09:16+0000", "id": "100003333155909" }
    email = me.data['email']
    artist = collection.find_one({"email":email})
    if artist:
        session['logged_in'] = True
        session['user_name'] = me.data['username']
        return redirect(url_for('index'))
    else:
      session['fb_id'] = me.data['id']
      session['fb_username'] = me.data['username']
      session['fb_email'] = me.data['email']
      return redirect(url_for('register'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.route('/<user_name>')
def job(user_name):
    artist = get_artist(user_name)
    if artist is not None:
        return render_template('artist_page.html', artist=artist)

    return "Error"

@app.route('/savetip', methods=['POST'])
def post_tip():
    try:
        amount = float(request.form['amount'])
    except:
        amount = 0.00

    tip = Tip(request.form['user_name'], amount, request.form['message'], request.form['email'], request.form['name'], datetime.datetime.now())
    save_tip(tip)
    return "OK"


def validate_new_artist(artist_form):
    if len(artist_form['artist_name']) == 0:
        return "Artist/Band Name is required"

    if len(artist_form['user_name']) == 0:
        return "Username is required"

    if is_username_unique(artist_form['user_name'], get_artists()) is False:
        return "Username already taken"

    if len(artist_form['email']) == 0:
        return "Email is required"

    if len(artist_form['password']) == 0:
        return "Password is required"

def validate_update_artist(artist_form):
    if len(artist_form['artist_name']) == 0:
        return "Artist/Band Name is required"

    if len(artist_form['user_name']) == 0:
        return "Username is required"

    if len(artist_form['email']) == 0:
        return "Email is required"


@app.route('/register', methods=['GET', 'POST'])
@app.route('/update/<user_name>', methods=['GET', 'POST'])
def edit(user_name = None):

    if request.method == 'POST':

        if user_name:
            message = validate_update_artist(request.form)
        else:
            message = validate_new_artist(request.form)

        if message is None:

            if user_name is None:
                qr_path = qrcode_string(config.DOMAIN + request.form['user_name'])
                artist = Artist(request.form['user_name'], request.form['artist_name'], request.form['email'], qr_path, request.form['password'], request.form['paypal_id'], default_tip_amount=request.form['default_tip_amount'])
                flash('Registered Successfully',category='success')
            else:
                artist = get_artist(user_name)
                artist.artist_name = request.form['artist_name']
                artist.email = request.form['email']
                artist.default_tip_amount = request.form['default_tip_amount']
                if session['fb_id']:
                  artist.fb_id = session['fb_id']

                if 'password' in request.form and len(request.form['password']) > 0:
                    artist.set_password(request.form['password'])

                flash('Updated Successfully',category='success')


            save_artist(artist)

            return redirect(url_for('index'))
        else:
            flash(message,category='error')
            return render_template('register.html', artist=None)


    else:
        if user_name:
            artist = get_artist(user_name)
            return render_template('register.html', artist=artist)
        elif 'fb_id' in session:
            artist = Artist(session['fb_username'],'', session['fb_email'], fb_id = session['fb_id']) 
            return render_template('register.html', artist=artist, register=True)
        else:
            return render_template('register.html', artist=None)



