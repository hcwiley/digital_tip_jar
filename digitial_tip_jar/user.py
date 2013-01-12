import json
from config import MONGODB_HOST, MONGODB_PORT
from pymongo import *
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, first_name, last_name, user_name, band_name, qr_path = '', password=''):
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.band_name = band_name
        self.qr_path = qr_path
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


    def __repr__(self):
        return json.dumps(self.__dict__)


def save_user(user):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['users']

    userFromDB = collection.find_one({"user_name": user.user_name})

    if userFromDB is None:
        collection.insert(user.__dict__)
    else:
        collection.update({"user_name": user.user_name}, user.__dict__)


def get_user(user_name):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['users']

    user = collection.find_one({"user_name": user_name})

    if user is None:
        return None

    user_to_return = User(user['first_name'], user['last_name'], user['user_name'], user['band_name'], qr_path=user['qr_path'])
    user_to_return.pw_hash = user['pw_hash']

    return user_to_return


def get_users():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['users']
    data = collection.find({})
    users = []

    for user in data:
        user_to_return = User(user['first_name'], user['last_name'], user['user_name'], user['band_name'], qr_path=user['qr_path'])
        user_to_return.pw_hash = user['pw_hash']

        users.append(user_to_return)


    return users

