import secrets

from flask import render_template, redirect, url_for, flash
from flask.globals import request

from musicrecs import db
from musicrecs import spotify_iface
from musicrecs.sql_models import Submission, Round
from musicrecs.enums import RoundStatus, MusicType
from musicrecs.exceptions import UserError, InternalError
from musicrecs.spotify import spotify_user
from musicrecs.external_auth.decorators import recover_after_auth

from musicrecs.main import bp
from musicrecs.main.forms import NewRoundForm, TrackrecForm, AlbumrecForm, PlaylistForm
from musicrecs.main.helpers import user_name_taken, get_snoozin_rec, get_shuffled_music_submissions


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    new_round_form = NewRoundForm()

    try:
        if new_round_form.validate_on_submit():
            # Get the new_round_form fields
            description = new_round_form.description.data
            music_type = new_round_form.music_type.data
            snoozin_rec_type = new_round_form.snoozin_rec_type.data

            # Add the round to the database
            new_round = Round(
                description=description,
                music_type=music_type,
                snoozin_rec_type=snoozin_rec_type,
                long_id=secrets.token_urlsafe(16)
            )
            db.session.add(new_round)
            db.session.commit()

            # Go to the page for the new round
            return redirect(url_for('main.round', long_id=new_round.long_id))

        elif new_round_form.errors:
            raise InternalError(new_round_form.errors)

    except UserError as e:
        flash(e, "warning")
    except InternalError as e:
        flash(e, "danger")

    return render_template('index.html', new_round_form=new_round_form)


@bp.route('/round/<string:long_id>', methods=["GET", "POST"])
def round(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Prepare the forms
    if round.music_type == MusicType.album:
        rec_form = AlbumrecForm()
        playlist_form = None
    elif round.music_type == MusicType.track:
        rec_form = TrackrecForm()
        playlist_form = PlaylistForm()
        playlist_form.playlist_name.data = round.description  # prefill
    else:
        raise Exception(f"Unknown music type {round.music_type}")

    if round.status == RoundStatus.submit:
        return render_template('round/submit_phase.html',
                               rec_form=rec_form,
                               round=round)
    elif round.status == RoundStatus.listen or round.status == RoundStatus.revealed:
        # Get the playlist
        if round.playlist_link:
            playlist = spotify_iface.get_playlist_from_link(round.playlist_link)
        else:
            playlist = None

        return render_template('round/listen_phase.html',
                               round=round,
                               music_submissions=get_shuffled_music_submissions(round),
                               playlist_form=playlist_form,
                               playlist=playlist,
                               revealed=RoundStatus.revealed)


@bp.route('/round/<string:long_id>/advance', methods=['POST'])
def round_advance(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Perform actions that are round phase transition specific
    if 'advance_to_listen' in request.form:
        try:
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
        except UserError as e:
            flash(e, "warning")
        except InternalError as e:
            flash(e, "danger")
    elif 'advance_to_revealed' in request.form:
        round.status = RoundStatus.revealed
        db.session.commit()

    # Go back to the round page
    return redirect(url_for('main.round', long_id=long_id))


@bp.route('/round/<string:long_id>/submit_rec', methods=['POST'])
def round_submit_rec(long_id):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Get the correct recommendation form
    if round.music_type == MusicType.album:
        rec_form = AlbumrecForm()
    elif round.music_type == MusicType.track:
        rec_form = TrackrecForm()
    else:
        raise InternalError(f"Unknown music type {round.music_type.name}")

    try:
        # Process the music recommendation
        if rec_form.validate_on_submit():
            # Get the rec_form fields
            user_name = rec_form.name.data
            spotify_link = rec_form.spotify_link.data

            # Verify form info
            if spotify_iface.spotify_link_invalid(round.music_type, spotify_link):
                raise UserError(f"Invalid spotify {round.music_type.name} link")
            elif user_name_taken(round, user_name):
                raise UserError(f"The name \"{user_name}\" is taken already for this round!")
            elif user_name == "snoozin":
                raise UserError("This town's only big enough for one snoozin...")

            # Add the submission to the database
            new_submission = Submission(
                spotify_link=spotify_link,
                user_name=user_name,
                round_id=round.id,
            )
            db.session.add(new_submission)
            db.session.commit()

            # Alert the user that the form was successfully submitted
            flash("Successfully submitted your recommendation: "
                  f"{spotify_iface.get_music_from_link(round.music_type, spotify_link)}",
                  "success")

            # Reload the round page
            return redirect(url_for('main.round', long_id=long_id))

        elif rec_form.errors:
            raise InternalError(rec_form.errors)

    except UserError as e:
        flash(e, "warning")
    except InternalError as e:
        flash(e, "danger")

    # Retain form entries when there was a mistake in the submission
    return render_template('round/submit_phase.html',
                           rec_form=rec_form,
                           round=round)


@bp.route('/round/<string:long_id>/create_playlist', methods=['GET', 'POST'])
@recover_after_auth()
def round_create_playlist(long_id, recovered_form_data=None):
    # Get the round from the long id
    round = Round.query.filter_by(long_id=long_id).first()

    # Make sure this is a 'track' round...or else making a playlist doesn't make
    # any sense
    assert round.music_type == MusicType.track

    # Get the form data
    if recovered_form_data:
        playlist_form = PlaylistForm(recovered_form_data)
    else:
        playlist_form = PlaylistForm()

    # Make the playlist!
    if playlist_form.validate():
        playlist_name = playlist_form.playlist_name.data

        # Get a list of the tracks in the round (in the 'shuffled' order)
        tracks = [track for _, track in get_shuffled_music_submissions(round)]

        # Make the playlist
        new_playlist = spotify_user.create_playlist(playlist_name, tracks)

        # Add the playlist to the database
        round.playlist_link = new_playlist.link
        db.session.commit()

        flash(f"Created a playlist for the round: {new_playlist.name}", "success")

    return redirect(url_for('main.round', long_id=long_id))
