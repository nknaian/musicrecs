import random
from typing import List, Tuple

from flask import flash, url_for
from flask.globals import request

from musicrecs import db
from musicrecs import spotify_iface
from musicrecs.database.models import Round
from musicrecs.spotify import spotify_user
import musicrecs.random_words.random_words as random_words
from musicrecs.spotify.item.spotify_music import SpotifyMusic
from musicrecs.spotify.item.spotify_playlist import SpotifyPlaylist
from musicrecs.enums import SnoozinRecType
from musicrecs.errors.exceptions import MusicrecsError
from musicrecs.external_auth.decorators import retry_after_auth


"""PUBLIC FUNCTIONS"""


def user_name_taken(round: Round, user_name: str) -> bool:
    for submission in round.submissions:
        if submission.user_name == user_name:
            return True
    return False


def get_abs_round_link(round: Round):
    rel_round_path = url_for('round.index', long_id=round.long_id)

    return '/'.join(path_part.strip('/') for path_part in [request.url_root, rel_round_path])


@retry_after_auth()
def create_playlist(round_long_id, name) -> SpotifyPlaylist:
    """Create playlist for the round

    Because this function is decorated with `retry_after_auth`, it must
    take as input the round long_id and use that to query the round, as opposed
    to being passed the round directly. This is because the round object seems to
    become stale in some way by the time the function is retried.
    """
    # Get the round from the long id
    round = Round.query.filter_by(long_id=round_long_id).first()

    # Get a list of the tracks in the round (in the 'shuffled' order)
    tracks = [track for _, track in get_shuffled_music_submissions(round)]

    # Make the playlist
    new_playlist = spotify_user.create_playlist(name, tracks)

    # Add the playlist to the database
    round.playlist_link = new_playlist.link
    db.session.commit()

    flash(f"Created a playlist for the round: {new_playlist.name}", "success")

    return new_playlist


# TODO: maybe we need to put in a max number of search attempts for buggy situations...
def get_snoozin_rec(round: Round) -> SpotifyMusic:
    """Get a random or similar music recommendation.

    - Get random music recommendations by searching a
      random 1 or 2 word phrase in spotify
    - Get similar music recommendations by using spotify's
      recommendation api
    """
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
        raise MusicrecsError(f"Unknown Snoozin rec type {round.snoozin_rec_type}")

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
