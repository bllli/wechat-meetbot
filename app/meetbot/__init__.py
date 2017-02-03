from flask import Blueprint

meetbot = Blueprint('meetbot', __name__)

from . import views