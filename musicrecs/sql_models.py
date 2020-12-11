from datetime import datetime
import enum
from musicrecs import db
from musicrecs.spotify.music import Music

class MusicType(enum.Enum):
    TRACK = "track"
    ALBUM = "album"

class RoundStatus(enum.Enum):
    PAST = "past"
    CURRENT = "current"
    NEXT = "next"

class SnoozinRecType(enum.Enum):
    RANDOM = "random"
    SIMILAR = "similar"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    submissions = db.relationship('Submission',
        backref=db.backref('user', lazy=True))

    def __repr__(self):
        return '<Submission %r>' % self.username

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    music = db.Column(db.String(50), nullable=False) # Store spotify url here

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)

    def __repr__(self):
        return '<Submission %r>' % self.id

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    music_type = db.Column(db.Enum(MusicType), nullable=False)
    round_status = db.Column(db.Enum(RoundStatus), nullable=False)
    snoozin_rec_type = db.Column(db.Enum(SnoozinRecType), nullable=False)
    snoozin_rec_search_term = db.Column(db.String(50))

    rec_group_id = db.Column(db.Integer, db.ForeignKey('rec_group.id'),
        nullable=False)
    submissions = db.relationship('Submission',
        backref=db.backref('round', lazy=True))

    created = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    def __repr__(self):
        return '<Round %r>' % self.id

class RecGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    rounds = db.relationship('Round',
        backref=db.backref('rec_group', lazy=True))

    def __repr__(self):
        return '<RecGroup %r>' % self.name