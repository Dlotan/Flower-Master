#!/usr/bin/env python
import os
if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app
from flask.ext.script import Manager
from app import db
from app.models import Users

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

@manager.command
def adduser(username):
    """ Register a new user. """

    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = Users(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


@manager.command
def addtestdata():
    """ Add test data for dev mode. """
    db.create_all()
    from app.models import GrowSessions
    from datetime import datetime
    session = GrowSessions(start_date=datetime.utcnow())
    db.session.add(session)
    db.session.commit()
    from app.models import FlowerDevices
    device_a = FlowerDevices(name='a', mac='amac', grow_session_id=session.id)
    db.session.add(device_a)
    device_b = FlowerDevices(name='b', mac='bmac', grow_session_id=session.id)
    db.session.add(device_b)
    db.session.commit()
    for _ in range(50):
        from app.models import FlowerData
        datapoint = FlowerData(
            timestamp=datetime.utcnow(),
            temperature=10.23,
            light=100,
            water=40.5,
            battery=90,
            ecb=0.5,
            ec_porus=0.6,
            dli=0.7,
            ea=0.8,
            flower_device_id=device_a.id,
        )
        db.session.add(datapoint)
    db.session.commit()
    print('Fake data added')


@manager.command
def dropall():
    """ Delete whole database. """
    db.drop_all()

if __name__ == '__main__':
    manager.run()