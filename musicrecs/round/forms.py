from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from musicrecs import spotify_iface

from musicrecs.enums import MusicType
from musicrecs.round.helpers import user_name_taken
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


class _UserName(object):
    """Validates that the field is a valid username.

    - Usernames can not be repeated in the round
    - Username cannot be "snoozin"
    """
    def __call__(self, form, field):
        if len(field.data) > MAX_USERNAME_LENGTH:
            raise ValidationError(f'Name too long, must be fewer than {MAX_USERNAME_LENGTH} characters')
        elif field.data == "snoozin":
            raise ValidationError('This town is only big enough for one snoozin...')
        elif user_name_taken(form._round, field.data):
            raise ValidationError("This name already is taken already for the round!")


"""FORMS"""


class RoundForm(FlaskForm):
    def __init__(self, round, formdata=None, **kwargs):
        self._round = round

        if formdata:
            super().__init__(formdata=formdata, **kwargs)
        else:
            super().__init__(**kwargs)


class TrackrecForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _UserName()])
    spotify_link = StringField(
        'Spotify Track URL',
        description=SPOTIFY_TRACK_URL_DESCRIPTION,
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit = SubmitField('Submit Track Recommendation')


class AlbumrecForm(RoundForm):
    name = StringField('What is your name?', validators=[DataRequired(), _UserName()])
    spotify_link = StringField(
        'Spotify Album URL',
        description=SPOTIFY_ALBUM_URL_DESCRIPTION,
        validators=[DataRequired(), _SpotifyLink()]
    )
    submit = SubmitField('Submit Album Recommendation')


class PlaylistForm(FlaskForm):
    """ATTRIBUTES"""
    max_name_length = SpotifyPlaylist.MAX_NAME_LENGTH

    """FIELDS"""
    name = StringField('Playlist Name', validators=[DataRequired(), Length(max=max_name_length)])
    submit = SubmitField('Create the playlist!')
