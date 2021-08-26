from flask import Blueprint

from musicrecs import cache

bp = Blueprint('main', __name__)


@bp.app_context_processor
def inject_main_vars():
    return dict(
        music_bg_imgs=cache.get("main_music_bg_imgs")
    )


from musicrecs.main import handlers
