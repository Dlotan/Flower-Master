from flask import render_template, flash
from flask.ext.login import login_required
from . import display


@display.route("/")
@login_required
def index():
    return render_template('/display/index.html')
