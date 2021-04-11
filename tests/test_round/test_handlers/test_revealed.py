from musicrecs.round.helpers import get_shuffled_user_name_list
import re

from flask.helpers import url_for

from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType
from musicrecs.database.helpers import add_guess_to_db, add_round_to_db, add_submission_to_db

from tests.test_round import RoundTestCase


class RoundRevealedTestCase(RoundTestCase):
    """Test GET to round.revealed route

    For an album round, and a track round, test that the submissions
    are present on the round page, and consist of the correct link - name pairs.
    """
    def test_album_revealed(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Albumrecs random round",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.revealed
        )

        # Add a couple submissions to the round
        add_submission_to_db(round.id, "Nick Jones", "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz")
        add_submission_to_db(round.id, "Jonie Nixon", "https://open.spotify.com/album/1vz94WpXDVYIEGja8cjFNa")
        add_submission_to_db(round.id, "snoozin", "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw")

        # Get the correct shuffled user name order
        shuffled_user_names = get_shuffled_user_name_list(round)

        # Add Nick Jones's guesses to the round, mixing up Jonie and snoozin
        # (NOTE: There is no testing as of now to verify that these
        # guesses added to the database are displayed correctly)
        add_guess_to_db(1, "Jonie Nixon", shuffled_user_names.index("snoozin"), False)
        add_guess_to_db(1, "snoozin", shuffled_user_names.index("Jonie Nixon"), False)
        add_guess_to_db(1, "Nick Jones", shuffled_user_names.index("Nick Jones"), True)

        # Verify that the round page contains the correct pairings of link with submitter
        response = self.client.get(url_for('round.revealed', long_id=round.long_id))
        self.assert_200(response)
        href_results = re.findall(r'<a href=(.+?)</a>', str(response.data))
        for href_result in href_results:
            if "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz" in href_result:
                self.assertIn("Nick Jones", href_result)
            elif "https://open.spotify.com/album/1vz94WpXDVYIEGja8cjFNa" in href_result:
                self.assertIn("Jonie Nixon", href_result)
            elif "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw" in href_result:
                self.assertIn("snoozin", href_result)
            else:
                raise Exception(f"Unknown link in href {href_result}")

    def test_track_revealed(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Albumrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.revealed
        )

        # Add a few submissions to the round
        add_submission_to_db(round.id, "John Doe", "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        add_submission_to_db(round.id, "Dory Johnson", "https://open.spotify.com/track/354K3xQPgALQEOiIYzAMat")
        add_submission_to_db(round.id, "snoozin", "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb")

        # Get the correct shuffled user name order
        shuffled_user_names = get_shuffled_user_name_list(round)

        # Add a John Doe's guesses to the round, mixing up Dory and snoozin
        # (NOTE: There is no testing as of now to verify that these
        # guesses added to the database are displayed correctly)
        add_guess_to_db(1, "Dory Johnson", shuffled_user_names.index("snoozin"), False)
        add_guess_to_db(1, "snoozin", shuffled_user_names.index("Dory Johnson"), False)
        add_guess_to_db(1, "John Doe", shuffled_user_names.index("John Doe"), True)

        # Verify that the round page contains the correct pairings of link with submitter
        response = self.client.get(url_for('round.revealed', long_id=round.long_id))
        self.assert_200(response)
        href_results = re.findall(r'<a href=(.+?)</a>', str(response.data))
        for href_result in href_results:
            if "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6" in href_result:
                self.assertIn("John Doe", href_result)
            elif "https://open.spotify.com/track/354K3xQPgALQEOiIYzAMat" in href_result:
                self.assertIn("Dory Johnson", href_result)
            elif "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb" in href_result:
                self.assertIn("snoozin", href_result)
            else:
                raise Exception(f"Unknown link in href {href_result}")
