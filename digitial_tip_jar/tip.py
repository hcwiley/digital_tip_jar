import json
from config import MONGODB_HOST, MONGODB_PORT
from pymongo import *
from utils import JSONEncoder
from bson.son import SON

class Tip:
    def __init__(self, artist_user_name, amount, message, email_address, full_name, timestamp):
        self.artist_user_name = artist_user_name
        self.amount = amount
        self.message = message
        self.email_address = email_address
        self.full_name = full_name
        self.timestamp = timestamp

    def __repr__(self):
        return json.dumps(self.__dict__, cls=JSONEncoder)

def save_tip(tip):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    collection.insert(tip.__dict__)

def get_tips_for_artist(artist_user_name):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    data = collection.find({"artist_user_name": artist_user_name}).sort("time", DESCENDING)
    tips = []

    for tip in data:
        tips.append(Tip(tip['artist_user_name'], tip['amount'], tip['message'], tip['email_address'], tip['full_name'], tip['timestamp']))

    return tips

def get_most_recent_tip():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    data = collection.find().sort("time", DESCENDING).limit(1)
    tips = []

    for tip in data:
        tips.append(Tip(tip['artist_user_name'], tip['amount'], tip['message'], tip['email_address'], tip['full_name'], tip['timestamp']))

    return tips[0]

def get_active_tippers():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']

    data = collection.aggregate([
        {"$group": {"_id": "$name", "total": {"$sum": "$email"}}},
        {"$sort": SON([("total", -1), ("_id", -1)])}
    ])

    tips = []
    count = 0
    for tip in data:
        if count > 5:
            break

        tips.append([tip['_id'], tip['total']])
        count = count + 1

    return tips


def get_generous_tippers():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']

    data = collection.aggregate([
        {"$group": {"_id": "$name", "total": {"$sum": "$amount"}}},
        {"$sort": SON([("total", -1), ("_id", -1)])}
    ])

    tips = []
    count = 0
    for tip in data:
        if count > 5:
            break

        tips.append([tip['_id'], tip['total']])
        count = count + 1

    return tips



