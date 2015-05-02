from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from .factory import db, login_manager


class Users(UserMixin, db.Model):
    __tablaname__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

""" Event stuff """


class Events(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.Text)
    type = db.Column(db.Text)
    args = db.Column(db.Text)


class EventLog(db.Model):
    __tablename__ = 'event_log'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.Text)
    type = db.Column(db.Text)
    args = db.Column(db.Text)
    comment = db.Column(db.Text)

""" Everything grow related """


class GrowSessions(db.Model):
    __tablename__ = 'grow_sessions'

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    days_grow_stage = db.Column(db.Integer)

    grow_stage_day_hours = db.Column(db.Integer, default=12)
    grow_stage_night_hours = db.Column(db.Integer, default=12)
    flower_stage_day_hours = db.Column(db.Integer, default=18)
    flower_stage_night_hours = db.Column(db.Integer, default=6)

    name = db.Column(db.Text)
    brand = db.Column(db.Text)
    num_plants = db.Column(db.Integer)
    square_centimeters = db.Column(db.Integer)
    gram_yield = db.Column(db.Integer)
    end_date = db.Column(db.DateTime)

    light_devices = db.relationship('LightDevices', back_populates='grow_session')
    watering_devices = db.relationship('WateringDevices', back_populates='grow_session')
    flower_devices = db.relationship('FlowerDevices', back_populates='grow_session')

    flower_data = db.relationship('FlowerData', back_populates='grow_session')

    @hybrid_property
    def is_active(self):
        return self.end_date is None

    @hybrid_property
    def flower_start_date(self):
        return self.start_date + timedelta(self.days_grow_stage)

    @hybrid_property
    def is_flower_stage(self):
        flower_start = self.start_date + timedelta(self.days_grow_stage)
        return datetime.utcnow() < flower_start

    @hybrid_property
    def is_grow_stage(self):
        flower_start = self.start_date + timedelta(self.days_grow_stage)
        return datetime.utcnow() >= flower_start

    @staticmethod
    def get_active_sessions():
        return GrowSessions.query.filter_by(end_date=None)


class LightDevices(db.Model):
    __tablename__ = 'light_devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    grow_session_id = db.Column(db.Integer, db.ForeignKey('grow_sessions.id'))
    grow_session = db.relationship('GrowSessions', back_populates='light_devices')


class WateringDevices(db.Model):
    __tablename__ = 'watering_devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    grow_session_id = db.Column(db.Integer, db.ForeignKey('grow_sessions.id'))
    grow_session = db.relationship('GrowSessions', back_populates='watering_devices')


class FlowerDevices(db.Model):
    __tablename__ = 'flower_devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    mac = db.Column(db.Text)
    is_active = db.Column(db.Boolean, index=True, default=True)

    grow_session_id = db.Column(db.Integer, db.ForeignKey('grow_sessions.id'))
    grow_session = db.relationship('GrowSessions', back_populates='flower_devices')
    flower_data = db.relationship('FlowerData',
                                  back_populates='flower_device',
                                  order_by='desc(FlowerData.timestamp)')

    @staticmethod
    def get_active():
        return FlowerDevices.query.filter_by(is_active=True).all()


class FlowerData(db.Model):
    __tablename__ = 'flower_data'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    temperature = db.Column(db.REAL)
    light = db.Column(db.Integer)
    water = db.Column(db.REAL)
    battery = db.Column(db.Integer)
    ecb = db.Column(db.REAL)
    ec_porus = db.Column(db.REAL)
    dli = db.Column(db.REAL)
    ea = db.Column(db.REAL)

    flower_device_id = db.Column(db.Integer, db.ForeignKey('flower_devices.id'))
    flower_device = db.relationship('FlowerDevices', back_populates='flower_data')

    grow_session_id = db.Column(db.Integer, db.ForeignKey('grow_sessions.id'))
    grow_session = db.relationship('GrowSessions', back_populates='flower_data')


    @staticmethod
    def new_flower_data(data, flower_device_id):
        flower_data = FlowerData(
            temperature=data['Temperature'],
            light=data['Light'],
            water=data['Water'],
            battery=data['Battery'],
            ecb=data['Ecb'],
            ec_porus=data['EcPorus'],
            dli=data['DLI'],
            ea=data['Ea'],
            flower_device_id=flower_device_id,
        )

        db.session.add(flower_data)
        db.session.commit()