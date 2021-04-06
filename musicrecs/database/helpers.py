import secrets

from musicrecs.database.models import Round, Submission
from musicrecs.enums import RoundStatus

from musicrecs import db


def add_round_to_db(description, music_type, snoozin_rec_type, status=RoundStatus.submit):
    """Add a round to the database with the given properties

    Return the newly added round object
    """

    round = Round(
        description=description,
        music_type=music_type,
        snoozin_rec_type=snoozin_rec_type,
        long_id=_create_round_long_id(),
        status=status
    )
    db.session.add(round)
    db.session.commit()

    return round


def add_submission_to_db(round_id, user_name, spotify_link):
    """Add a submission to the database with the given properties

    Return the newly added submission object
    """
    submission = Submission(
        spotify_link=spotify_link,
        user_name=user_name,
        round_id=round_id
    )
    db.session.add(submission)
    db.session.commit()

    return submission


"""PRIVATE FUNCTIONS"""


def _create_round_long_id():
    return secrets.token_urlsafe(16)
