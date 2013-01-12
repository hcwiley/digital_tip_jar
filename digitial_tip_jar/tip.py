import json
from config import *
from pymongo import *
from utils import JSONEncoder
from bson.son import SON
from artist import get_artist

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

def get_total_tip_amount_for_artist(artist_user_name):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    data = collection.find({"artist_user_name": artist_user_name}).sort("timestamp", DESCENDING)
    sum = 0.0
    for tip in data:
        sum = sum + tip['amount']
    return sum

def get_tips_for_artist(artist_user_name, size=RECENT_TIPS_SIZE):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    data = collection.find({"artist_user_name": artist_user_name}).sort("timestamp", DESCENDING)
    tips = []
    count = 0
    for tip in data:
        if count > size:
            break
        tips.append(Tip(tip['artist_user_name'], tip['amount'], tip['message'], tip['email_address'], tip['full_name'], tip['timestamp']))
        count = count + 1
    return tips

def get_most_recent_tip():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']
    data = collection.find().sort("timestamp", DESCENDING).limit(MOST_RECENT_SIZE)

    for tip in data:
        recent_tip_info = {}
        recent_tip_info['name'] = tip['full_name']
        recent_tip_info['artist_user_name'] = tip['artist_user_name']
        recent_tip_info['band_name'] = get_artist(tip['artist_user_name']).artist_name
        recent_tip_info['time'] = tip['timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")
        return recent_tip_info

    return None

def get_active_tippers():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']

    data = collection.aggregate([
        {"$group": {"_id": "$full_name", "total": {"$sum": "$email"}}},
        {"$sort": SON([("total", -1), ("_id", -1)])}
    ])

    tips = []
    count = 0
    for tip in data['result']:
        if count > 5:
            break

        tips.append({ "name":tip['_id'], "total_tips": tip['total']  })
        count = count + 1

    print "gat: %s" % tips
    return tips


def get_generous_tippers():
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['tips']

    data = collection.aggregate([
        {"$group": {"_id": "$full_name", "total": {"$sum": "$amount"}}},
        {"$sort": SON([("total", -1), ("_id", -1)])}
    ])

    tips = []
    count = 0
    for tip in data['result']:
        if count > 5:
            break

        tips.append({ "name":tip['_id'], "total_amount": tip['total']  })
        count = count + 1

    print "ggt: %s" % tips
    return tips



