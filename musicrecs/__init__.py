import os
import random
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from musicrecs.spotify.spotify import Spotify

# Create flask application and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
db = SQLAlchemy(app)

# Create bootstrap flask app
Bootstrap(app)

# import sql models and create database
from musicrecs.sql_models import User, Submission, Round
db.create_all()

# Seed random
random.seed(time.time())

# Create spotify interface
spotify_iface = Spotify()

from musicrecs import views
