from multiprocessing.pool import ThreadPool
from ..models import FlowerDevices, FlowerData
from .. import db
from . import hardware
from .flower_power import get_flower_data


@hardware.route('/flower/data')
def flowerpower_data():
    future_flower_data = []
    i = 0
    for flower_device in FlowerDevices.get_active():
        pool = ThreadPool(processes=1)
        future_flower_data.append((flower_device.id, pool.apply_async(get_flower_data, [flower_device.mac])))
    for async_result in future_flower_data:
        data = async_result[1].get()
        FlowerData.new_flower_data(data, async_result[0])
        flower_data = FlowerData(
            temperature=data['Temperature'],
            light=data['Light'],
            water=data['Water'],
            battery=data['Battery'],
            ecb=data['Ecb'],
            ec_porus=data['EcPorus'],
            dli=data['DLI'],
            ea=data['Ea'],
            flower_device_name=async_result[0],
        )
        db.session.add(flower_data)
        db.session.commit()
        i += 1
    return "Scanned " + str(i) + " Devices "