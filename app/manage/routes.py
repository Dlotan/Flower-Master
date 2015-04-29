from flask import render_template
from flask.ext.login import login_required
from . import manage



@manage.route('/')
@login_required
def index():
    return render_template('/manage/index.html')