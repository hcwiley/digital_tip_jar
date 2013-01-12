import config
from flask import request, render_template, redirect, url_for, flash, session
from digitial_tip_jar import app
from utils import qrcode_string, is_username_unique
from artist import *
from flask_oauth import OAuth

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
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('index'))
 
@app.route('/fblogin')
def fblogin():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/fblogin/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return redirect(url_for('index'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.route('/<user_name>')
def job(user_name):
    artist = get_artist(user_name)
    if artist is not None:
        return render_template('artist_page.html', artist=artist)

    return "Error"

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
                # [XXX] Hardcoded shit
                qr_path = qrcode_string("http://digitaltipjar.homemadebyrobots.org/"+request.form['user_name'])
                artist = Artist(request.form['user_name'], request.form['artist_name'], request.form['email'], qr_path, request.form['password'], request.form['paypal_id'])
                flash('Registered Successfully',category='success')
            else:
                artist = get_artist(user_name)
                artist.artist_name = request.form['artist_name']
                artist.email = request.form['email']

                if 'password' in request.form and len(request.form['password']) > 0:
                    artist.set_password(request.form['password'])

                flash('Updated Successfully',category='success')


            save_artist(artist)

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



