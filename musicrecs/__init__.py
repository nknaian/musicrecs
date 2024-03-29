import random
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_caching import Cache
from flask_apscheduler import APScheduler

from musicrecs.spotify.spotify import Spotify
from musicrecs.config import Config


# Create sqlalchemy database
db = SQLAlchemy()

# Create cache
cache = Cache()

# Create scheduler
scheduler = APScheduler()

# Create 'client credentials' spotify interface
spotify_iface = Spotify()

# Seed random
random.seed(time.time())


def create_app(config_class=Config):
    # Create flask application from config
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize spotify as long as we're not testing
    if not app.config["TESTING"]:
        spotify_iface.init_sp()

    # Initialize database
    db.init_app(app)

    # Initialize cache
    cache.init_app(app)

    # Initialize scheduler and start background tasks
    scheduler.init_app(app)

    from musicrecs.main import background_tasks
    scheduler.start()

    # Register blueprints
    from musicrecs.main import bp as main_bp
    app.register_blueprint(main_bp)

    from musicrecs.round import bp as round_bp
    app.register_blueprint(round_bp)

    from musicrecs.user import bp as user_bp
    app.register_blueprint(user_bp)

    from musicrecs.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    if app.config["TESTING"]:
        from musicrecs.test import bp as test_bp
        app.register_blueprint(test_bp)

    # Create bootstrap flask app
    Bootstrap(app)

    # Create flask session
    Session(app)

    # Create all tables in the database
    with app.app_context():
        db.create_all()

    return app
