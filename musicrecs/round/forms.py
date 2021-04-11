import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from musicrecs import spotify_iface

from musicrecs.enums import MusicType
from musicrecs.round.helpers import GUESS_LINE_PATTERN, get_guesser_names, get_user_names, get_music_numbers
from musicrecs.database.models import MAX_USERNAME_LENGTH
from musicrecs.spotify.item.spotify_playlist import SpotifyPlaylist


"""FORM DESCRIPTIONS"""


SPOTIFY_TRACK_URL_DESCRIPTION = "(ex: http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6)"
SPOTIFY_ALBUM_URL_DESCRIPTION = "(ex: https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz)"


"""CUSTOM VALIDATOR CLASSES"""


class _SpotifyLink(object):
    """Validates that the field is a valid spotify link using the
    spotify interface.
    """
    def __call__(self, form, field):
        if spotify_iface.spotify_link_invalid(form._round.music_type, field.data):
            if form._round.music_type == MusicType.track:
                description = SPOTIFY_TRACK_URL_DESCRIPTION
            elif form._round.music_type == MusicType.album:
                description = SPOTIFY_ALBUM_URL_DESCRIPTION

            raise ValidationError(f"Invalid spotify {form._round.music_type.name} link ... {description}")


class _NewUserName(object):
    """Validates that the field is a valid new username.

    - Usernames can not be repeated in the round
    - Username cannot be "snoozin"
    """
    def __call__(self, form, field):
        if len(field.data) > MAX_USERNAME_LENGTH:
            raise ValidationError(f'Name too long, must be fewer than {MAX_USERNAME_LENGTH} characters')
        elif field.data.lower().strip() == "snoozin":
            raise ValidationError('This town is only big enough for one snoozin...')
        elif field.data in get_user_names(form._round):
            raise ValidationError("This name already is taken already for the round!")


class _GuessUserName(object):
    """Validates that the field is a username in the round.

    - Usernames can not be repeated in the round
    - Username cannot be "snoozin"
    """
    def __call__(self, form, field):
        if field.data not in get_user_names(form._round):
            raise ValidationError(f"No user named {field.data} submitted a rec!")
        elif field.data in get_guesser_names(form._round):
            raise ValidationError(f"A guess from user name {field.data} has already been submitted!")


class _GuessField(object):
    """Validates that the guess field the user fills out has the correct format
    """
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
        'Spotify Track URL',
        description=SPOTIFY_TRACK_URL_DESCRIPTION,
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit = SubmitField('Submit Track Recommendation')


class AlbumrecForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _NewUserName()])
    spotify_link = StringField(
        'Spotify Album URL',
        description=SPOTIFY_ALBUM_URL_DESCRIPTION,
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit = SubmitField('Submit Album Recommendation')


class GuessForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _GuessUserName()])
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
