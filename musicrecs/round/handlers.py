from flask import render_template, redirect, url_for, flash
from flask.globals import request

from musicrecs import db
from musicrecs import spotify_iface
from musicrecs.database.models import Submission, Round
from musicrecs.database.helpers import add_submission_to_db
from musicrecs.enums import RoundStatus, MusicType
from musicrecs.errors.exceptions import MusicrecsAlert, MusicrecsError

from . import bp
from .forms import TrackrecForm, AlbumrecForm, PlaylistForm
from .helpers import get_snoozin_rec, get_shuffled_music_submissions, get_abs_round_link, create_playlist


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

    # Process the submission form
    if rec_form.validate_on_submit():
        # Add the submission to the database
        add_submission_to_db(round.id, rec_form.name.data, rec_form.spotify_link.data)

        # Alert the user that the form was successfully submitted
        flash("Successfully submitted your recommendation: "
              f"{spotify_iface.get_music_from_link(round.music_type, rec_form.spotify_link.data)}",
              "success")

        # Redirect back to the round after successful submission
        return redirect(url_for('round.submit', long_id=long_id))

    elif rec_form.errors:
        flash("There were errors in your rec submission", "warning")

    return render_template('round/submit_phase.html',
                           round_link=get_abs_round_link(round),
                           rec_form=rec_form,
                           round=round)


@bp.route('/round/<string:long_id>/listen', methods=["GET", "POST"])
def listen(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Make sure this is the correct handler for the round's current status
    if round.status not in [RoundStatus.listen, RoundStatus.revealed]:
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
    elif playlist_form and playlist_form.validate_on_submit():
        create_playlist(long_id, playlist_form.name.data)
        return redirect(url_for('round.listen', long_id=long_id))
    # Notify the user if there were errors
    elif playlist_form and playlist_form.errors:
        flash("There were errors in your rec submission", "warning")

    return render_template('round/listen_phase.html',
                           round_link=get_abs_round_link(round),
                           round=round,
                           music_submissions=get_shuffled_music_submissions(round),
                           playlist_form=playlist_form,
                           playlist=playlist)


@bp.route('/round/<string:long_id>/revealed', methods=["GET", "POST"])
def revealed(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Currently there is no difference at the python level in how the
    # listen and revealed statuses are handled...
    return redirect(url_for('round.listen', long_id=round.long_id))


@bp.route('/round/<string:long_id>/advance', methods=['POST'])
def advance(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Perform actions that are round phase transition specific
    if 'advance_to_listen' in request.form:
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

    elif 'advance_to_revealed' in request.form:
        round.status = RoundStatus.revealed
        db.session.commit()

    # Go back to the round page
    return redirect(url_for('round.index', long_id=long_id))