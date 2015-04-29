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
def maketestdata():
    """ Make test data for dev mode. """
    db.drop_all()
    db.create_all()
    from app.models import GrowSessions
    from datetime import datetime, timedelta
    session = GrowSessions(name='test_session',
                           start_date=datetime.utcnow())
    db.session.add(session)
    db.session.commit()
    from app.models import FlowerDevices
    device_a = FlowerDevices(name='flower_device_a', mac='amac', grow_session_id=session.id)
    db.session.add(device_a)
    device_b = FlowerDevices(name='flower_device_b', mac='bmac', grow_session_id=session.id)
    db.session.add(device_b)
    db.session.commit()
    for i in range(50):
        from app.models import FlowerData
        datapoint = FlowerData(
            timestamp=datetime.utcnow()-timedelta(i),
            temperature=10.23 + i*0.1,
            light=100,
            water=40.5 - i*0.5,
            battery=90 - i,
            ecb=0.5,
            ec_porus=0.6,
            dli=0.7,
            ea=0.8,
            flower_device_id=device_a.id,
        )
        db.session.add(datapoint)
    user = Users(username='Dlotan', password='dlotan')
    db.session.add(user)
    db.session.commit()
    print('Fake data made')


@manager.command
def dropall():
    """ Delete whole database. """
    db.drop_all()

if __name__ == '__main__':
    manager.run()