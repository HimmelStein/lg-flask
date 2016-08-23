import os
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from pprint import pprint
import tasks.chinese.clgnet as ch_processer

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import ChBible


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/make_net_from_chsnt', methods=['GET', 'POST'])
def make_net_from_chsnt():
    print('in /make_net_from_chsnt', request.args)
    chSnt = request.args.get('snt')
    print('server received:', chSnt)
    depGraph = ch_processer.get_raw_ldg(chSnt)
    pprint(depGraph)
    return jsonify(depGraph)

if __name__ == '__main__':
    app.run(debug=True)
