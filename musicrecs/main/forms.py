from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField, BooleanField, IntegerField
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
    scheduled_round = BooleanField('Scheduled round?')
    scheduled_round_interval = IntegerField('Scheduled interval (seconds)', validators=[])
    submit = SubmitField('Create Round')
