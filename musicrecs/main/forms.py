from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from musicrecs.enums import SnoozinRecType, MusicType


class NewRoundForm(FlaskForm):
    description = TextAreaField('Describe the round', validators=[DataRequired()])
    music_type = SelectField(
        'Which type of music should be recommended?',
        choices=MusicType.choices(),
        coerce=MusicType.coerce
    )
    snoozin_rec_type = SelectField(
        'Which type of recommendation should snoozin make?',
        choices=SnoozinRecType.choices(),
        coerce=SnoozinRecType.coerce
    )
    submit = SubmitField('Create Round')


class TrackrecForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    spotify_link = StringField(
        'Spotify Track URL',
        description="(ex: http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6)"
    )
    submit = SubmitField('Submit Track Recommendation')


class AlbumrecForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    spotify_link = StringField(
        'Spotify Album URL',
        description="(ex: https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz)"
    )
    submit = SubmitField('Submit Album Recommendation')


class PlaylistForm(FlaskForm):
    # TODO: It would be nice to limit the number of characters entered here
    # to MAX_PLAYLIST_NAME_LENGTH. When using the 'Length' validator, I can't
    # seem to get a message to pop up, like happens for 'DataRequired'. So
    # the experience for the user ends up being too clunky to be worth it. And
    # still, it would be better to just limit the chars...where 'Length' validator
    # checks after the form is submitted
    playlist_name = StringField('Playlist Name', validators=[DataRequired()])
    submit = SubmitField('Create the playlist!')
