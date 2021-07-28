import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.core import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from musicrecs import spotify_iface

from musicrecs.round.helpers import GUESS_LINE_PATTERN, get_user_names, get_music_numbers, get_current_user_submission
from musicrecs.database.models import MAX_USERNAME_LENGTH
from musicrecs.spotify.item.spotify_playlist import SpotifyPlaylist


"""CONSTANTS"""

GUESSER_NAME_PLACEHOLDER = "Please select your name"


"""CUSTOM VALIDATOR CLASSES"""


class _SpotifyLink(object):
    """Validates that the field is a valid spotify link using the
    spotify interface.
    """
    def __call__(self, form, field):
        if spotify_iface.spotify_link_invalid(form._round.music_type, field.data):
            raise ValidationError(f"Invalid spotify {form._round.music_type.name} link.")

        # Shorten the field to the base spotify link
        field.data = spotify_iface.get_music_from_link(form._round.music_type, field.data).link


class _NewUserName(object):
    """Makes sure that the field is a valid new username.

    - Usernames will not have beginning or trailing whitespace
    - Usernames cannot be too long
    - Usernames cannot be repeated in the round
    - Username cannot be "snoozin"
    """
    def __call__(self, form, field):
        # Strip beginning and trailing whitespace from the user name
        field.data = field.data.strip()

        # Get the current user's user_name in the round
        current_user_submission = get_current_user_submission(form._round)
        current_user_user_name = current_user_submission.user_name if current_user_submission is not None else None

        # Validate
        if len(field.data) > MAX_USERNAME_LENGTH:
            raise ValidationError(f'Name too long, must be fewer than {MAX_USERNAME_LENGTH} characters')
        elif field.data.lower() == "snoozin":
            raise ValidationError('This town is only big enough for one snoozin...')
        elif field.data in get_user_names(form._round) and field.data != current_user_user_name:
            raise ValidationError("This name already is taken already for the round!")


class _GuessUserName(object):
    """Validates that the field is user_name that hasn't guessed yet"""
    def __call__(self, form, field):
        if field.data == GUESSER_NAME_PLACEHOLDER:
            raise ValidationError(GUESSER_NAME_PLACEHOLDER)


class _GuessField(object):
    """Validates that the guess field the user fills out has the correct format"""
    def __call__(self, form, field):
        user_names_guessed = []
        music_nums_guessed = []
        for i, line in enumerate(field.data.splitlines()):
            match = re.match(GUESS_LINE_PATTERN, line)
            if not match:
                raise ValidationError(f"On line {i}: Incorrect formatting")
            else:
                # Validate the user name
                user_name = match.group(1)
                if user_name not in get_user_names(form._round):
                    raise ValidationError(f"On line {i}: User name {user_name} is not in this round!")
                else:
                    user_names_guessed.append(user_name)

                # Validate the track number
                music_num = int(match.group(2))
                if music_num not in get_music_numbers(form._round):
                    raise ValidationError(f"On line {i}: {music_num} is not a valid track number")
                else:
                    music_nums_guessed.append(music_num)

        # Validate all user names
        missing_user_names = get_user_names(form._round).difference(set(user_names_guessed))
        if missing_user_names:
            raise ValidationError(f"User names {missing_user_names} are missing from the guess")

        if len(user_names_guessed) > len(get_user_names(form._round)):
            raise ValidationError("Duplicate user names are present")

        # Validate all track numbers
        missing_music_nums = get_music_numbers(form._round).difference(set(music_nums_guessed))
        if missing_music_nums:
            raise ValidationError(f"Music numbers {missing_music_nums} are missing from the guess")

        if len(music_nums_guessed) > len(get_music_numbers(form._round)):
            raise ValidationError("Duplicate track numbers are present")


"""FORMS"""


class RoundForm(FlaskForm):
    def __init__(self, round, formdata=None, **kwargs):
        self._round = round

        if formdata:
            super().__init__(formdata=formdata, **kwargs)
        else:
            super().__init__(**kwargs)


class TrackrecForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _NewUserName()])
    spotify_link = StringField(
        'Spotify Track Link',
        description="Start typing to search for music, or directly input "
                    "a spotify track link (ex: http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6)",
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit_rec = SubmitField('Submit Track Recommendation')


class AlbumrecForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _NewUserName()])
    spotify_link = StringField(
        'Spotify Album Link',
        description="Start typing to search for music, or directly input "
                    "a spotify album link (ex: https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz)",
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit_rec = SubmitField('Submit Album Recommendation')


class GuessForm(RoundForm):
    name = SelectField(choices=[GUESSER_NAME_PLACEHOLDER], validators=[_GuessUserName()])
    guess_field = TextAreaField(
        'Pair each recommender with their rec number',
        render_kw={"rows": 3},
        validators=[DataRequired(), _GuessField()])
    submit_guess = SubmitField('Guess')


class PlaylistForm(FlaskForm):
    """ATTRIBUTES"""
    max_name_length = SpotifyPlaylist.MAX_NAME_LENGTH

    """FIELDS"""
    name = StringField('Playlist Name', validators=[DataRequired(), Length(max=max_name_length)])
    submit_playlist = SubmitField('Create the playlist!')
