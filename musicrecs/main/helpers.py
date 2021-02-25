import random
from typing import List, Tuple

from musicrecs import db
from musicrecs import spotify_iface
import musicrecs.random_words.random_words as random_words
from musicrecs.spotify.item.spotify_music import SpotifyMusic
from musicrecs.enums import SnoozinRecType
from musicrecs.sql_models import Round
from musicrecs.exceptions import InternalError


"""PUBLIC FUNCTIONS"""


def user_name_taken(round: Round, user_name: str) -> bool:
    for submission in round.submissions:
        if submission.user_name == user_name:
            return True
    return False


# TODO: maybe we need to put in a max number of search attempts for buggy situations...
def get_snoozin_rec(round: Round):
    snoozin_rec = None
    if round.snoozin_rec_type == SnoozinRecType.random:
        rw_gen = random_words.RandomWords()
        num_words = random.randint(1, 2)

        search_term = ""
        while snoozin_rec is None:
            search_term = " ".join(
                rw_gen.get_random_words(num_words)
            )
            snoozin_rec = spotify_iface.search_for_music(round.music_type, search_term)

        # Set the round's search term
        round.snoozin_rec_search_term = search_term
        db.session.commit()

    elif round.snoozin_rec_type == SnoozinRecType.similar:
        snoozin_rec = spotify_iface.recommend_music(round.music_type, _get_music_list(round))
    else:
        raise InternalError("Unknown Snoozin rec type")

    return snoozin_rec


def get_shuffled_music_submissions(round: Round) -> List[Tuple[str, SpotifyMusic]]:
    """Get a shuffled list of tuples of the username paired with
    the music they submitted for the round
    """
    # Make a list large enough to hold the submissions
    shuffled_music_submissions = [None] * len(round.submissions)

    # Shuffle the submissions if they haven't been already
    _shuffle_music_submissions(round)

    # Add a tuple of user_name and music at the 'shuffled position' of the new list
    for submission in round.submissions:
        shuffled_music_submissions[submission.shuffled_pos] = (
            submission.user_name,
            spotify_iface.get_music_from_link(round.music_type, submission.spotify_link)
        )

    # Make sure that every spot in the list was filled
    assert all(shuffled_music_submissions)

    return shuffled_music_submissions


"""PRIVATE FUNCTIONS"""


def _shuffle_music_submissions(round: Round, reshuffle=False):
    """Shuffle the submissions in the round by storing a random
    'shuffled_pos' in each db entry.

    By default, this will have no effect if the submissions have
    already been shuffled, but that behavior can be overridden by
    passing `reshuffle=True`.
    """
    # Bail if we've already shuffled it `reshuffle` was not specified
    if (round.submissions[0].shuffled_pos is not None) and (not reshuffle):
        return

    # Create a random order on integers from 0 to the number of submissions
    # Ex for 6 submissions: `[4, 3, 5, 0, 1, 2]` (first submitted should be
    # shuffled to the fourth spot, second submitted should be shuffled to
    # the third spot etc.)
    rand_order = list(range(len(round.submissions)))
    random.shuffle(rand_order)

    # Assign each submission a 'shuffled position' using the `rand_order`
    for submission, rand_num in zip(
        round.submissions,
        rand_order
    ):
        submission.shuffled_pos = rand_num

    # commit the shuffled possitions to the database
    db.session.commit()


def _get_music_list(round: Round) -> List[SpotifyMusic]:
    """Get a list of the music in the round in the order it was submitted"""
    return [
        spotify_iface.get_music_from_link(
            round.music_type, submission.spotify_link
        ) for submission in round.submissions
    ]
