from musicrecs.database.helpers import add_submission_to_db
from musicrecs.database.models import Round
from musicrecs.round.helpers import get_snoozin_rec
from musicrecs.enums import RoundStatus

from musicrecs import scheduler, db


def add_sec_interval_job(round: Round, interval_sec):
    """Call the round advance task every `interval_sec`
    seconds.
    """
    scheduler.add_job(job_id(round),
                      task,
                      kwargs=dict(round=round),
                      trigger='interval',
                      seconds=interval_sec)


def job_id(round: Round):
    """Background task identifer based on round id"""
    return f'sched_round_advance_{round.id}'


def task(round):
    """The round advance background task.

    It will advance to listen first, adding snoozin's
    submission. Then it will advance to revealed and
    remove the job so it's not called again.
    """
    with scheduler.app.app_context():
        if round.status == RoundStatus.submit:
            # Add snoozin's rec:
            add_submission_to_db(round.id, None, "snoozin", get_snoozin_rec(round).link)

            # Advance to 'listen' phase
            round.status = RoundStatus.listen
            db.session.commit()

        elif round.status == RoundStatus.listen:
            # Advance to 'revealed' phase
            round.status = RoundStatus.revealed
            db.session.commit()

            # We've reached the last phase...stop this job
            scheduler.remove_job(job_id(round))
