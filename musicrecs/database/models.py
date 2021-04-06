from datetime import datetime
from sqlalchemy.orm import validates

from musicrecs import db
from musicrecs.enums import MusicType, SnoozinRecType, RoundStatus
from musicrecs.errors.exceptions import MusicrecsError


'''Storage Constants'''

MAX_SPOTIFY_LINK_LENGTH = 100
MAX_USERNAME_LENGTH = 50
MAX_LONG_ID_LENGTH = 50


'''SQL Classes'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    submissions = db.relationship('Submission', backref=db.backref('user', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_link = db.Column(db.String(MAX_SPOTIFY_LINK_LENGTH), nullable=False)
    user_name = db.Column(db.String(MAX_USERNAME_LENGTH))
    shuffled_pos = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)

    @validates('spotify_link')
    def validate_spotify_link(self, key, spotify_link):
        if len(spotify_link) > MAX_SPOTIFY_LINK_LENGTH:
            raise MusicrecsError(f"Spotify link greater than storage limit of {MAX_SPOTIFY_LINK_LENGTH} characters.")
        return spotify_link

    @validates('user_name')
    def validate_user_name(self, key, user_name):
        if len(user_name) > MAX_USERNAME_LENGTH:
            raise MusicrecsError(f"User name greater than storage limit of {MAX_USERNAME_LENGTH} characters.")
        return user_name

    def __repr__(self):
        return '<Submission %r>' % self.id


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_id = db.Column(db.String(MAX_LONG_ID_LENGTH), unique=True)
    description = db.Column(db.Text, nullable=False)
    music_type = db.Column(db.Enum(MusicType), nullable=False)
    status = db.Column(db.Enum(RoundStatus), default=RoundStatus.submit)
    snoozin_rec_type = db.Column(db.Enum(SnoozinRecType), nullable=False)
    snoozin_rec_search_term = db.Column(db.String(50))
    playlist_link = db.Column(db.String(MAX_SPOTIFY_LINK_LENGTH))

    submissions = db.relationship('Submission', backref=db.backref('round', lazy=True))

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @validates('long_id')
    def validate_long_id(self, key, long_id):
        if len(long_id) > MAX_LONG_ID_LENGTH:
            raise MusicrecsError(f"long id greater than storage limit of {MAX_LONG_ID_LENGTH} characters.")
        return long_id

    @validates('playlist_link')
    def validate_playlist_link(self, key, playlist_link):
        if playlist_link is not None and len(playlist_link) > MAX_SPOTIFY_LINK_LENGTH:
            raise MusicrecsError(f"playlist link greater than storage limit of {MAX_SPOTIFY_LINK_LENGTH} characters.")
        return playlist_link

    def __repr__(self):
        return '<Round %r>' % self.id
