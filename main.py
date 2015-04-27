from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
import flower_power
from multiprocessing.pool import ThreadPool
import sqlite3
from flask import Flask
import argparse
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pi/workspaces/pycharm/flower_master/flowerpin.db'
db = SQLAlchemy(app)


class FlowerData(db.Model):
    id = Column(Integer, primary_key=True)

db.create_all()

@app.route("/")
def main_page():
    return 'Hello World'

app.debug = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flower Master')
    args = parser.parse_args()
    app.run()


"""
pool = ThreadPool(processes=1)
print "Get flower data"
flower_async_result = pool.apply_async(flower_power.get_flower_data, ['A0:14:3D:08:B4:90'])
flower_result = flower_async_result.get()"""