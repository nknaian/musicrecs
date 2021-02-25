import os


class Config(object):
    """This class is used to configure the flask app using
    default settings and environment variable settings
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'
