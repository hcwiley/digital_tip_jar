import config
from flask import request, render_template
from digitial_tip_jar import app
from utils import slugify
from user import *




@app.route('/', methods=['POST','GET'])
def index():
    users = get_users()
    return render_template('index.html', users=users)



