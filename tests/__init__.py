import unittest
from unittest.mock import Mock
from flask.helpers import url_for

import flask_testing

from musicrecs.config import Config
from musicrecs.spotify.item.spotify_music import SpotifyMusic
import musicrecs.spotify.spotify_user as sp_user

from musicrecs import spotify_iface

from musicrecs import create_app, db, scheduler


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

        # Mock the user being logged out
        self.unauth_dummy_user()

        # Mock get_music_from_link
        spotify_iface.get_music_from_link = Mock(side_effect=self._mock_get_music_from_link)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        scheduler.shutdown()

    """MOCK SPOTIFY USER INTERFACE"""

    DUMMY_USER_SP_ID = "12345ABC"
    DUMMY_USER_DISPLAY_NAME = "Dummy User"

    def _raise_sp_test_exception(self, *args):
        """Raises an exception to authorize at the fake sp auth route"""
        raise sp_user.SpotifyUserAuthFailure(auth_url=url_for("test.fake_sp_auth"))

    def auth_dummy_user(self, *args):
        sp_user.get_user_id = Mock(side_effect=lambda *args: self.DUMMY_USER_SP_ID)
        sp_user.is_authenticated = Mock(side_effect=lambda *args: True)
        sp_user.get_user_display_name = Mock(side_effect=lambda *args: self.DUMMY_USER_DISPLAY_NAME)
        sp_user.logout = Mock(side_effect=self.unauth_dummy_user)

    def unauth_dummy_user(self, *args):
        sp_user.get_user_id = Mock(side_effect=self._raise_sp_test_exception)
        sp_user.is_authenticated = Mock(side_effect=lambda *args: False)
        sp_user.get_user_display_name = Mock(side_effect=self._raise_sp_test_exception)
        sp_user.auth_new_user = Mock(side_effect=self.auth_dummy_user)

    """MOCK SPOTIFY MUSIC"""

    def _mock_get_music_from_link(self, *args):
        """Return a spotify music object whose link attribute
        is equal to the link passed in and that has a dummy img url
        """
        music_mock = Mock(spec=SpotifyMusic)
        music_mock.link = args[1]
        music_mock.img_url = ""
        return music_mock
