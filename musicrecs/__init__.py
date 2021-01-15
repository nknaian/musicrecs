import os
import random
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_session import Session

from musicrecs.spotify.spotify import Spotify

# Create flask application and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
db = SQLAlchemy(app)

# Create bootstrap flask app
Bootstrap(app)

# Create flask session
Session(app)

# import sql models and create database
from musicrecs.sql_models import User, Submission, Round
db.create_all()

# Seed random
random.seed(time.time())

# Create 'client credentials' spotify interface
spotify_iface = Spotify()

from musicrecs import views
