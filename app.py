import os
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from tasks.lgutil import snt_ldg2db

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import ChBible


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
