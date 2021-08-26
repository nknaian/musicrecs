from musicrecs.database.helpers import add_round_to_db, add_submission_to_db
from musicrecs.enums import MusicType, SnoozinRecType, RoundStatus

from tests import MusicrecsTestCase


class MainTestCase(MusicrecsTestCase):
    def setUp(self):
        super().setUp()

        # create a bunch of revealed rounds with a submission
        for i in range(100):
            # Add a round to the database
            round = add_round_to_db(
                description="Albumrecs random round",
                music_type=MusicType.album,
                snoozin_rec_type=SnoozinRecType.random,
                status=RoundStatus.revealed
            )

            # Add a couple submissions to the round
            add_submission_to_db(round.id, None, "Nick Jones", "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz")
