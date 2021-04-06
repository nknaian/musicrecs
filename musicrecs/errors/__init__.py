from flask import Blueprint

bp = Blueprint('errors', __name__)

from musicrecs.errors import handlers
