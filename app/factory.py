import os
from celery import Celery
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name, with_blueprint=True):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not app.config['DEBUG'] and not app.config['TESTING']:
        # configure logging for production

        # send standard logs to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    if with_blueprint:
        from .auth.routes import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        from .display.routes import display as display_blueprint
        app.register_blueprint(display_blueprint)

        from .hardware.routes import hardware as hardware_blueprint
        app.register_blueprint(hardware_blueprint)

        from .manage.routes import manage as manage_blueprint
        app.register_blueprint(manage_blueprint)

    return app


def create_celery_app(app=None):
    app = app or create_app(os.getenv('FLASK_CONFIG') or 'default', False)
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery