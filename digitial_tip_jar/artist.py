import json
from config import MONGODB_HOST, MONGODB_PORT
from pymongo import *
from werkzeug.security import generate_password_hash, check_password_hash

class Artist:
    def __init__(self, user_name, artist_name, email, qr_path = '', password='', paypal_id='', fb_id='', default_tip_amount=0.00):
        self.user_name = user_name
        self.artist_name = artist_name
        self.email = email
        self.qr_path = qr_path
        self.set_password(password)
        self.paypal_id = paypal_id
        self.fb_id = fb_id
        self.default_tip_amount = default_tip_amount

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


    def __repr__(self):
        return json.dumps(self.__dict__)


def save_artist(artist):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['artists']

    artistFromDB = collection.find_one({"user_name": artist.user_name})

    if artistFromDB is None:
        collection.insert(artist.__dict__)
    else:
        collection.update({"user_name": artist.user_name}, artist.__dict__)


def get_artist(user_name):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['artists']

    artist = collection.find_one({"user_name": user_name})

    if artist is None:
        return None

    artist_to_return = Artist(artist['user_name'], artist['artist_name'], artist['email'], qr_path=artist['qr_path'], paypal_id=artist['paypal_id'], fb_id = artist['fb_id'])
    artist_to_return.pw_hash = artist['pw_hash']

    return artist_to_return


def get_artists():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['artists']
    data = collection.find({})
    artists = []

    for artist in data:
        artist_to_return = Artist(artist['user_name'], artist['artist_name'], artist['email'], qr_path=artist['qr_path'], paypal_id=artist['paypal_id'], fb_id = artist['fb_id'])
        artist_to_return.pw_hash = artist['pw_hash']

        artists.append(artist_to_return)


    return artists

