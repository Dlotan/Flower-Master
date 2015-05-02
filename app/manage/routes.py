from flask import render_template, Blueprint
from flask.ext.login import login_required


manage = Blueprint('manage', __name__)


@manage.route('/')
@login_required
def index():
    return render_template('/manage/index.html')