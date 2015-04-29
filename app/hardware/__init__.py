from flask import Blueprint

hardware = Blueprint('hardware', __name__)

from . import routes