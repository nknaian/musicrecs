from musicrecs.user.helpers import current_user_id
import re
from flask import render_template, redirect, url_for, flash
from flask.globals import request

from musicrecs import db
from musicrecs import spotify_iface
from musicrecs.database.models import Submission, Round
from musicrecs.database.helpers import add_submission_to_db
from musicrecs.enums import RoundStatus, MusicType
from musicrecs.errors.exceptions import MusicrecsAlert, MusicrecsError

from . import bp
from .forms import GuessForm, TrackrecForm, AlbumrecForm, PlaylistForm
from .helpers import get_current_user_submission, process_guess_form, get_snoozin_rec, \
    create_playlist, get_user_names, get_guesser_names


@bp.route('/round/<string:long_id>', methods=["GET", "POST"])
def index(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    if round.status == RoundStatus.submit:
        return redirect(url_for('round.submit', long_id=round.long_id))
    elif round.status == RoundStatus.listen:
        return redirect(url_for('round.listen', long_id=round.long_id))
    elif round.status == RoundStatus.revealed:
        return redirect(url_for('round.revealed', long_id=round.long_id))
    else:
        raise MusicrecsError(f"Unknown round status {round.status}")


@bp.route('/round/<string:long_id>/submit', methods=["GET", "POST"])
def submit(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Make sure this is the correct handler for the round's current status
    if round.status != RoundStatus.submit:
        raise MusicrecsAlert(f"This round is currently in the {round.status.name} phase...",
                             redirect_location=url_for(f'round.{round.status.name}', long_id=round.long_id))

    # Get data from the rec form
    if round.music_type == MusicType.album:
        rec_form = AlbumrecForm(round)
    elif round.music_type == MusicType.track:
        rec_form = TrackrecForm(round)
    else:
        raise MusicrecsError(f"Unknown music type {round.music_type}")

    # Get the currently logged in user's submission
    current_user_submission = get_current_user_submission(round)

    # Process the submission form
    if rec_form.validate_on_submit():
        # Change the user's submission
        if current_user_submission is not None:
            current_user_submission.user_name = rec_form.name.data
            current_user_submission.spotify_link = rec_form.spotify_link.data
            db.session.commit()
        # Add the submission to the database
        else:
            add_submission_to_db(round.id, current_user_id(), rec_form.name.data, rec_form.spotify_link.data)

        # Alert the user that the form was successfully submitted
        flash("Successfully submitted your recommendation: "
              f"{spotify_iface.get_music_from_link(round.music_type, rec_form.spotify_link.data)}",
              "success")

        # Redirect back to the round after successful submission
        return redirect(url_for('round.submit', long_id=long_id))

    elif rec_form.errors:
        flash("There were errors in your rec submission", "warning")

    # Deal with the current user's submission
    current_user_music = None
    if current_user_submission is not None:
        # Get music object for the user's submssion
        current_user_music = spotify_iface.get_music_from_link(round.music_type, current_user_submission.spotify_link)

        # Change the submit button text to reflect that this will change their submission
        rec_form.submit_rec.label.text = rec_form.submit_rec.label.text.replace("Submit", "Change")

        # Pre-fill form with current choice for user name
        rec_form.name.data = current_user_submission.user_name

    return render_template('round/submit_phase.html',
                           rec_form=rec_form,
                           round=round,
                           current_user_music=current_user_music)


@bp.route('/round/<string:long_id>/listen', methods=["GET", "POST"])
def listen(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Make sure this is the correct handler for the round's current status
    if round.status != RoundStatus.listen:
        raise MusicrecsAlert(f"This round is currently in the {round.status.name} phase...",
                             redirect_location=url_for(f'round.{round.status.name}', long_id=round.long_id))

    # Prepare the playlist form
    if round.music_type == MusicType.album:
        playlist_form = None
    elif round.music_type == MusicType.track:
        playlist_form = PlaylistForm()
    else:
        raise MusicrecsError(f"Unknown music type {round.music_type}")

    # Get the playlist if it's already been created
    playlist = None
    if round.playlist_link:
        playlist = spotify_iface.get_playlist_from_link(round.playlist_link)
    # If the playlist form has been submitted, then create the playlist and
    # reload the round
    elif playlist_form and playlist_form.submit_playlist.data and playlist_form.validate():
        create_playlist(long_id, playlist_form.name.data)
        return redirect(url_for('round.listen', long_id=long_id))
    # Notify the user if there were errors
    elif playlist_form and playlist_form.errors:
        flash("There were errors in your rec submission", "warning")

    # Process guess submissions
    guess_form = GuessForm(round)

    guess_form.name.choices.extend(list(set(get_user_names(round)) - set(get_guesser_names(round))))

    if guess_form.submit_guess.data and guess_form.validate():
        # Add the user's guesses within the form to the database
        process_guess_form(round, guess_form)

        # Alert the user that the guess was submitted successfully
        flash("Successfully submitted your guess", "success")

        return redirect(url_for('round.listen', long_id=round.long_id))

    elif guess_form.errors:
        flash("There were errors in your guess", "warning")
    else:
        # Prefill the usernames, with the appropriate number of rows
        guess_form.guess_field.render_kw["rows"] = len(round.submissions)
        guess_form.guess_field.data = "\n".join([f"{submission.user_name}: " for submission in round.submissions])

    return render_template('round/listen_phase.html',
                           round=round,
                           playlist_form=playlist_form,
                           playlist=playlist,
                           guess_form=guess_form)


@bp.route('/round/<string:long_id>/revealed', methods=["GET", "POST"])
def revealed(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Make sure this is the correct handler for the round's current status
    if round.status != RoundStatus.revealed:
        raise MusicrecsAlert(f"This round is currently in the {round.status.name} phase...",
                             redirect_location=url_for(f'round.{round.status.name}', long_id=round.long_id))

    # Get the round playlist if one was made
    if round.playlist_link:
        playlist = spotify_iface.get_playlist_from_link(round.playlist_link)
    else:
        playlist = None

    return render_template('round/revealed_phase.html',
                           round=round,
                           playlist=playlist)


@bp.route('/round/<string:long_id>/advance', methods=['POST'])
def advance(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Perform actions that are round phase transition specific
    if 'advance_to_listen' in request.form and round.status == RoundStatus.submit:
        # Add snoozin's rec:
        new_submission = Submission(
            spotify_link=get_snoozin_rec(round).link,
            user_name="snoozin",
            round_id=round.id,
        )
        db.session.add(new_submission)

        # Advance to 'listen' phase
        round.status = RoundStatus.listen
        db.session.commit()

    elif 'advance_to_revealed' in request.form and round.status == RoundStatus.listen:
        round.status = RoundStatus.revealed
        db.session.commit()

    # Go back to the round page
    return redirect(url_for('round.index', long_id=long_id))


@bp.route('/round/spotify_search', methods=['POST'])
def spotify_search():
    """Search interface for javascript frontend
    function 'get_spotify_search_results'
    """
    # POST request
    if request.method == 'POST':
        # Get values from post request
        search_text = request.get_json()["search_text"]
        music_type = MusicType[request.get_json()["music_type"]]

        # Initialize response dict
        response_dict = {"music_results": [], "invalid_link": False}

        # Get the corresponding list of music to the search text. If the text
        # is an open spotify link, then attempt to get the music from it.
        # Otherwise, just search for the text in spotify and get a list of results.
        if re.match(r'https*://open.spotify.com/', search_text):
            if spotify_iface.spotify_link_invalid(music_type, search_text):
                response_dict["invalid_link"] = True
            else:
                music = spotify_iface.get_music_from_link(music_type, search_text)
                response_dict["music_results"] = [music.format_for_response_dict()]
        elif search_text:
            music_results = spotify_iface.search_for_music(music_type, search_text, num_results=20)
            response_dict["music_results"] = [music.format_for_response_dict() for music in music_results]

        return response_dict, 200
