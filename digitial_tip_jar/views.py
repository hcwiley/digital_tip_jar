import config
from flask import request, render_template
from digitial_tip_jar import app



@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')



