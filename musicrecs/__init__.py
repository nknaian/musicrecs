import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create flask application and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

# import sql models and create database
from musicrecs.sql_models import User, Submission, Round, RecGroup
db.create_all()

from musicrecs import music_recs