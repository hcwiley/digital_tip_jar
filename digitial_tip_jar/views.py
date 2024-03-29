import config
from flask import request, render_template, redirect, url_for, flash, session, jsonify
from digitial_tip_jar import app
from utils import qrcode_string, is_username_unique
from artist import *
from flask_oauth import OAuth
import datetime
from tip import *
from PIL import Image
from werkzeug import secure_filename
import os

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

@app.route('/tips')
def tip_activity():
    return render_template('tip_activity.html', most_recent=get_most_recent_tip(), most_popular_bands=get_most_popular_bands(), top_patrons=get_active_tippers(), most_generous_patrons=get_generous_tippers())

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
            user = get_artist(user_name)
            if user.is_admin:
              session['is_admin'] = True
            session['user_name'] = user_name
            session['logged_in'] = True
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    session.pop('logged_in', None)
    session.pop('fb_id', None)
    session.pop('fb_username', None)
    session.pop('fb_email', None)
    session.pop('is_admin', None)
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
      session['user_name'] = me.data['username']
      return redirect(url_for('edit'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


def allowed_file(filename):
    return '.' in filename and\
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/<user_name>/update', methods=['POST','GET'])
def user_update(user_name):
    if 'logged_in' in session and 'user_name' in session and session['user_name'] == user_name:
        artist = get_artist(user_name)

        if request.method == 'POST':

            message = validate_update_artist(request.form)

            if message is None:
                file = request.files['profile']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    img.thumbnail(IMAGE_SIZE, Image.ANTIALIAS)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], user_name + '_profile.jpg'), 'JPEG')
                    pic_url = STATIC_URL + 'profile/' + user_name + '_profile.jpg'
                else:
                    pic_url = artist.pic_url


                artist.artist_name = request.form['artist_name']
                artist.email = request.form['email']
                artist.default_tip_amount = float(request.form['default_tip_amount'])
                artist.pic_url = pic_url
                if 'fb_id' in session:
                    artist.fb_id = session['fb_id']

                if 'password' in request.form and len(request.form['password']) > 0:
                    artist.set_password(request.form['password'])

                flash('Updated Successfully',category='success')

                save_artist(artist)

                return redirect(url_for('index'))
            else:
                flash(message,category='error')
                return render_template('artist_update.html', artist=artist, os=os)


        else:
            if artist is not None:
                return render_template('artist_update.html', artist=artist, os=os)

    return "Error"

@app.route('/<user_name>/activity')
def user_activity(user_name):
    if 'logged_in' in session and 'user_name' in session and session['user_name'] == user_name:
        artist = get_artist(user_name)
        if artist is not None:
            return render_template('artist_activity.html', artist=artist, tips=get_tips_for_artist(user_name), total_tips=get_total_tip_amount_for_artist(user_name))

    return "Error"

@app.route('/<user_name>/qrcode')
def user_qrcode(user_name):
    if 'logged_in' in session and 'user_name' in session and session['user_name'] == user_name:
        artist = get_artist(user_name)
        if artist is not None:
            return render_template('qrcode.html', artist=artist)

    return "Error"

@app.route('/<user_name>')
def user_profile(user_name):
    artist = get_artist(user_name)
    if artist is not None:
        return render_template('artist_page.html', artist=artist, tips=get_tips_for_artist(user_name))

    return "Error"



@app.route('/savetip', methods=['POST'])
def post_tip():
    try:
        amount = float(request.form['amount'])
    except:
        amount = 0.00

    tip = Tip(request.form['user_name'], amount, request.form['message'], request.form['email'], request.form['name'], datetime.datetime.utcnow())
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

    if len(artist_form['email']) == 0:
        return "Email is required"


@app.route('/register', methods=['GET', 'POST'])
def edit():
       
    if request.method == 'POST':

        message = validate_new_artist(request.form)

        if message is None:
            file = request.files['profile']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img.thumbnail(IMAGE_SIZE, Image.ANTIALIAS)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['user_name'] + '_profile.jpg'), 'JPEG')
                pic_url = STATIC_URL + 'profile/' +request.form['user_name']+ '_profile.jpg'
            else:
                pic_url = None

            qr_path = qrcode_string(config.DOMAIN + request.form['user_name'])
            artist = Artist(request.form['user_name'], request.form['artist_name'], request.form['email'], qr_path, request.form['password'], request.form['paypal_id'], default_tip_amount=request.form['default_tip_amount'], pic_url=pic_url)
            flash('Registered Successfully',category='success')

            save_artist(artist)
            return redirect(url_for('index'))
        else:
            flash(message,category='error')
            return render_template('register.html', artist=None)


    else:
        if 'fb_id' in session:
            artist = Artist(session['fb_username'],'', session['fb_email'], fb_id = session['fb_id']) 
            return render_template('register.html', artist=artist)
        else:
            return render_template('register.html', artist=None)



