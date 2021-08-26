import os
import sys
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

    # Initialize ngrok
    _init_ngrok(app)

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


def _init_ngrok(app):
    """Initialize ngrok if desired for development environment"""
    if app.config.get("ENV") == "development" and \
            os.environ.get("USE_NGROK", "False") == "True":

        # pyngrok will only be installed, and should only ever be initialized, in a dev environment
        from pyngrok import ngrok

        # Create the ngrok tunnel on the first run of the app
        if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
            # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
            # when starting the server
            port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

            # Open a ngrok tunnel to the dev server
            public_url = ngrok.connect(port).public_url
            print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Retrieve the ngrok public url upon reloads and save to app config
        else:
            public_url = ngrok.get_tunnels()[0].public_url

        # Save the public url to the app config
        app.config["PUBLIC_URL"] = public_url
