from flask import url_for

from musicrecs.database.helpers import add_user_to_db

from tests.test_user import UserTestCase


class UserProfileTestCase(UserTestCase):
    """Test GET to the 'user.profile' route
    """

    def test_get_user_profile(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Visit profile page. Verify that the text 'Log in' is on the page
        response = self.client.get(url_for('user.profile'))
        self.assert_200(response)
        self.assertIn(bytes(f'Hello {self.DUMMY_USER_DISPLAY_NAME}!', 'utf-8'), response.data)
