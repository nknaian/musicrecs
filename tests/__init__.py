import unittest

import flask_testing

from musicrecs.config import Config
from musicrecs import create_app, db


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED = False


class MusicrecsTestCase(flask_testing.TestCase, unittest.TestCase):
    """Base test case class for all tests in musicrecs. Creates app
    using TestingConfig and sets up/tears down a fresh sqlalchemy
    database for use during the tests.
    """
    def create_app(self):
        # pass in test configuration
        return create_app(TestingConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
