from flask import render_template, Blueprint
from flask.ext.login import login_required

from ..models import GrowSessions
from ..tasks import async_bla

display = Blueprint('display', __name__)


@display.route("/")
@login_required
def status():
    print("start1")
    async_bla.delay()
    return render_template('display/status.html', grow_sessions=GrowSessions.get_active_sessions())