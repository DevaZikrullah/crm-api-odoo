from flask import Flask,request,Blueprint,jsonify,render_template,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
import psycopg2
import os
from werkzeug.utils import secure_filename
import uuid
import datetime
from flask_cors import CORS
from flask_wtf import CSRFProtect



load_dotenv()

UPLOAD_FOLDER = 'attachments'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/wh'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'])
cur = conn.cursor()
CORS(app)
csrf = CSRFProtect(app)

@app.cli.command('test')
def test():
    print('work')

from api import routes

