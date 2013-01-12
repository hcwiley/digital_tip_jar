import json
from config import MONGODB_HOST, MONGODB_PORT
from pymongo import *

class User:
    def __init__(self, first_name, last_name, user_name, band_name):
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.band_name = band_name

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

    return User(user['first_name'], user['last_name'], user['user_name'], user['band_name'])


def get_users():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['users']
    data = collection.find({})
    users = []

    for user in data:
        users.append(User(user['first_name'], user['last_name'], user['user_name'], user['band_name']))


    return users

