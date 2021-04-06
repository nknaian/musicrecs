from flask import Blueprint

bp = Blueprint('round', __name__)

from musicrecs.round import handlers
