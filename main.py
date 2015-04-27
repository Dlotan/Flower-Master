import flower_power
from multiprocessing.pool import ThreadPool
import sqlite3


def insert_into_db(light, temperature, water, battery):
    dbconn = sqlite3.connect("test.db")
    try:
        c = dbconn.cursor()
        c.execute("CREATE Table IF NOT EXISTS flower_data (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, light real, "
                  "temperature real, water real, battery real)")
        c.execute("INSERT INTO flower_data (light, temperature, water, battery) VALUES (?,?,?,?)",
                  (light, temperature, water, battery))
        dbconn.commit()
        print("Database written")
    finally:
        dbconn.close()


pool = ThreadPool(processes=1)
print "Get flower data"
flower_result = pool.apply_async(flower_power.get_flower_data, ['A0:14:3D:08:B4:90'])
result = flower_result.get()
for name in result:
    print name + " : " + str(result[name])