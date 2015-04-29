from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from sqlalchemy import Column, Integer, Text, REAL, DATETIME
import flower_power
from multiprocessing.pool import ThreadPool
from flask import Flask
import argparse
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pi/workspaces/pycharm/flower_master/flowerpin.db'
db = SQLAlchemy(app)


class FlowerDevice(db.Model):
    id = Column(Integer, primary_key=True)
    mac = Column(Text, unique=False)
    name = Column(Text, unique=False)
    session = Column(Integer, unique=False)


class FlowerData(db.Model):
    id = Column(Integer, primary_key=True)
    timestamp = Column(DATETIME, unique=False, default=datetime.now)
    temperature = Column(REAL, unique=False)
    light = Column(Integer, unique=False)
    water = Column(REAL, unique=False)
    battery = Column(Integer, unique=False)
    ecb = Column(REAL, unique=False)
    ec_porus = Column(REAL, unique=False)
    dli = Column(REAL, unique=False)
    ea = Column(REAL, unique=False)
    flower_device_name = Column(Text, unique=False)
    session = Column(Integer, unique=False)


db.create_all()

api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(FlowerData, methods=['GET'])


@app.route('/')
def main_page():
    return "Hello World!"

"""'A0:14:3D:08:B4:90'"""
@app.route('/request/flower')
def collect_flowerpower_data():
    async_results = []
    i = 0
    for flower_device in FlowerDevice.query.all():
        pool = ThreadPool(processes=1)
        async_results.append((flower_device.name, flower_device.session,
                              pool.apply_async(flower_power.get_flower_data, [flower_device.mac])))
    for async_result in async_results:
        result = async_result[2].get()
        flower_data = FlowerData(
            temperature=result['Temperature'],
            light=result['Light'],
            water=result['Water'],
            battery=result['Battery'],
            ecb=result['Ecb'],
            ec_porus=result['EcPorus'],
            dli=result['DLI'],
            ea=result['Ea'],
            flower_device_name=async_result[0],
            session=async_result[1],
        )
        db.session.add(flower_data)
        db.session.commit()
        i += 1
    return "Scanned " + str(i) + " Devices " + str(datetime.now())

app.debug = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flower Master')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=8080)
