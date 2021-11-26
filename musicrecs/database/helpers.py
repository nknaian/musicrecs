import secrets

from flask.helpers import url_for

from musicrecs.database.models import Guess, Round, Submission, User
from musicrecs.enums import RoundStatus
from musicrecs.errors.exceptions import MusicrecsAlert

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


def add_submission_to_db(round_id, user_id, user_name, spotify_link):
    """Add a submission to the database with the given properties

    Return the newly added submission object
    """
    if Submission.query.filter_by(user_name=user_name, round_id=round_id).first() or \
            (user_id is not None and Submission.query.filter_by(user_id=user_id, round_id=round_id).first()):
        round = Round.query.filter_by(id=round_id).first()
        raise MusicrecsAlert("You've already submitted!",
                             redirect_location=url_for(f'round.{round.status.name}', long_id=round.long_id))

    submission = Submission(
        spotify_link=spotify_link,
        user_id=user_id,
        user_name=user_name,
        round_id=round_id,
    )
    db.session.add(submission)
    db.session.commit()

    return submission


def add_guess_to_db(submission_id, user_name, music_num, correct):
    """Add the guess to the database"""
    guess = Guess(
        submission_id=submission_id,
        user_name=user_name,
        music_num=music_num,
        correct=correct
    )
    db.session.add(guess)
    db.session.commit()

    return guess


def add_user_to_db(spotify_user_id, display_name):
    user = User(
        spotify_user_id=spotify_user_id,
        display_name=display_name
    )
    db.session.add(user)
    db.session.commit()

    return user


def lookup_user_in_db(spotify_user_id) -> User:
    return User.query.filter_by(spotify_user_id=spotify_user_id).first()


"""PRIVATE FUNCTIONS"""


def _create_round_long_id():
    return secrets.token_urlsafe(16)
