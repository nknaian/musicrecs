from musicrecs.database.helpers import add_round_to_db, add_submission_to_db, add_user_to_db
from musicrecs.database.models import Submission, User
from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType
from musicrecs.errors.exceptions import MusicrecsAlert


from tests.test_database import DatabaseTestCase


class SubmissionsTestCase(DatabaseTestCase):
    """Test possible issues with adding submissions
    to the database
    """
    def test_user_name_double_submit(self):
        """Test that the same user_name can't be used in
        two submissions to the same round (This would break the round!)
        """
        # Add a round to the database
        round = add_round_to_db(
            description="Trackrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.submit
        )

        # Add a submission by the user
        add_submission_to_db(
            round.id,
            None,
            "the_user",
            "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        )

        # Add another submission by the same user, expect exception
        self.assertRaises(
            MusicrecsAlert,
            add_submission_to_db,
            round.id,
            None,
            "the_user",
            "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUother"
        )

        # Verify that only the first submission was added to the database
        submissions = Submission.query.all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].spotify_link, "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

    def test__user_double_submit(self):
        """Test that the same logged in user can't add two submissions
        to the same round (This would break the round!)
        """
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Add a round to the database
        round = add_round_to_db(
            description="Trackrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.submit
        )

        user = User.query.all()[0]

        # Add a submission by the user
        add_submission_to_db(
            round.id,
            user.id,
            self.DUMMY_USER_DISPLAY_NAME,
            "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        )

        # Add another submission by the same user, expect exception
        self.assertRaises(
            MusicrecsAlert,
            add_submission_to_db,
            round.id,
            user.id,
            "doesn't matter",
            "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUother"
        )

        # Verify that only the first submission was added to the database
        submissions = Submission.query.all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].spotify_link, "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
