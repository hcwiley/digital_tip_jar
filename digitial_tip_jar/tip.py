import json
from config import MONGODB_HOST, MONGODB_PORT
from pymongo import *
from utils import JSONEncoder

class Tip:
    def __init__(self, band_user_name, amount, message, email_address, full_name, timestamp):
        self.band_user_name = band_user_name
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

def get_tips_for_band(band_user_name):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['digital_tip_jar']
    collection = db['users']
    data = collection.find({"band_user_name": band_user_name}).sort("time", DESCENDING)
    tips = []

    for tip in data:
        tips.append(Tip(tip['band_user_name'], tip['amount'], tip['message'], tip['email_address'], tip['full_name'], tip['timestamp']))


    return tips

