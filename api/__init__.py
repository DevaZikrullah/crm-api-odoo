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

database=os.environ['DB_NAME']
username=os.environ['USERNAME']
password=os.environ['PASSWORD']
url=os.environ['URL']

CORS(app)
csrf = CSRFProtect(app)

@app.cli.command('test')
def test():
    print('work')

from api import routes

