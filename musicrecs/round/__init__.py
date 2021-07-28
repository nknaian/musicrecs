from flask import Blueprint

from .helpers import round_created_date, get_abs_round_link, get_shuffled_music_submissions


bp = Blueprint('round', __name__)


@bp.app_context_processor
def inject_round_vars():
    return dict(
        round_created_date=round_created_date,
        get_abs_round_link=get_abs_round_link,
        get_shuffled_music_submissions=get_shuffled_music_submissions
    )


from musicrecs.round import handlers
