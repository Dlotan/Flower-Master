from flask import render_template
from flask.ext.login import login_required
from ..models import GrowSessions
from . import display


@display.route("/")
@login_required
def index():
    return render_template('/display/index.html')


@display.route("/status")
@login_required
def status():
    return render_template('display/status.html', grow_sessions=GrowSessions.get_active_sessions())