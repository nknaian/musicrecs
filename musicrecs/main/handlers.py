from flask import render_template, redirect, url_for, flash


from musicrecs.database.helpers import add_round_to_db

from . import bp, schedule_round_advance
from .forms import NewRoundForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')


@bp.route('/create_round', methods=['GET', 'POST'])
def create_round():
    new_round_form = NewRoundForm()

    if new_round_form.validate_on_submit():
        # Add the round to the database
        create_round = add_round_to_db(new_round_form.description.data,
                                       new_round_form.music_type.data,
                                       new_round_form.snoozin_rec_type.data)

        if new_round_form.scheduled_round.data is True:
            schedule_round_advance.add_sec_interval_job(create_round, new_round_form.scheduled_round_interval.data)

        # Go to the page for the new round
        return redirect(url_for('round.index', long_id=create_round.long_id))

    elif new_round_form.errors:
        flash("There were errors in your new round submission", "warning")

    return render_template('main/create_round.html', new_round_form=new_round_form)


@bp.route('/about', methods=['GET'])
def about():
    return render_template('main/about.html')
