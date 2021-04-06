from flask import render_template, redirect, url_for, flash

from musicrecs.database.helpers import add_round_to_db

from . import bp
from .forms import NewRoundForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    new_round_form = NewRoundForm()

    if new_round_form.validate_on_submit():
        # Add the round to the database
        new_round = add_round_to_db(new_round_form.description.data,
                                    new_round_form.music_type.data,
                                    new_round_form.snoozin_rec_type.data)

        # Go to the page for the new round
        return redirect(url_for('round.index', long_id=new_round.long_id))

    elif new_round_form.errors:
        flash("There were errors in your new round submission", "warning")

    return render_template('index.html', new_round_form=new_round_form)
