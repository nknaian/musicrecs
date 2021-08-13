from musicrecs.enums import MusicType, SnoozinRecType
from flask.helpers import url_for

from musicrecs.database.helpers import add_round_to_db, add_user_to_db

from tests.test_user import UserTestCase


class UserLogoutTestCase(UserTestCase):
    """Test flows involving POST to the user.logout route
    """
    def test_logout_user_from_mainindex(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Make POST to logout page from the main index page
        response = self.client.post(
            url_for('user.logout'),
            data=dict(logout_from_spotify="Log out"),
            follow_redirects=True,
            headers={
                "Referer": url_for('main.index')  # set 'request.referrer' ('Referer' is not a typo lol)
            }
        )

        # Verify that post was successful and redirected back to the main page
        # NOTE: I have a hacky solution of puttting in a string of text I know
        # will be on the main page. I can't figure out how to check the url
        # of the response so this is the best I could come up with.
        self.assert200(response)
        self.assertIn(bytes("Welcome to Musicrecs!", 'utf-8'), response.data)

    def test_logout_user_from_userprofile(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Make POST to logout page from the user profile page
        response = self.client.post(
            url_for('user.logout'),
            data=dict(logout_from_spotify="Log out"),
            follow_redirects=True,
            headers={
                "Referer": url_for('user.profile')  # set 'request.referrer' ('Referer' is not a typo lol)
            }
        )

        # Verify that post was successful and redirected back to the main page
        # NOTE: I have a hacky solution of puttting in a string of text I know
        # will be on the main page. I can't figure out how to check the url
        # of the response so this is the best I could come up with.
        self.assert200(response)
        self.assertIn(bytes("Welcome to Musicrecs!", 'utf-8'), response.data)

    def test_logout_user_from_round(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Add a round to logout from
        round = add_round_to_db(
            description="Trackrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
        )

        # Make POST to logout page from the round page
        response = self.client.post(
            url_for('user.logout'),
            data=dict(logout_from_spotify="Log out"),
            follow_redirects=True,
            headers={
                # set 'request.referrer' ('Referer' is not a typo lol)
                "Referer": url_for('round.index', long_id=round.long_id)
            }
        )

        # Verify that post was successful and redirected back to the round page
        # NOTE: I have a hacky solution of puttting in a string of text I know
        # will be on the round page. I can't figure out how to check the url
        # of the response so this is the best I could come up with.
        self.assert200(response)
        self.assertIn(bytes("Share the Round Link", 'utf-8'), response.data)
