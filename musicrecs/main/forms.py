from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
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
