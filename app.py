import os
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from pprint import pprint
import tasks.chinese.clgnet as ch_processer
import tasks.german.dlgnet as de_processer
import tasks.english.elgnet as en_processer

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


@app.route('/get_graph_net', methods=['GET', 'POST'])
def get_graph_net():
    Table = request.args.get('table').split()[1]
    Snt = request.args.get('snt')
    Lan = request.args.get('lan')
    print('Table', Table)
    if Lan == 'ch':
        snt, graphNet = ch_processer.get_graph_net(Snt)
        pprint(graphNet)
        return jsonify({'snt': snt, 'graph': graphNet})
    elif Lan == 'de':
        snt, graphNet = de_processer.get_graph_net(Snt)
        pprint(graphNet)
        return jsonify({'snt': snt, 'graph': graphNet})
    elif Lan == 'en':
        graphNet = en_processer.get_graph_net(Snt)
        pprint(graphNet)
        return jsonify(graphNet)
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
