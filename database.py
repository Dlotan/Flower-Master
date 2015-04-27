import sqlite3


def insert_into_db(light, temperature, water, battery):
    conn = sqlite3.connect("test.db")
    try:
        c = conn.cursor()
        c.execute("CREATE Table IF NOT EXISTS flower_data (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, light real, "
                  "temperature real, water real, battery real)")
        c.execute("INSERT INTO flower_data (light, temperature, water, battery) VALUES (?,?,?,?)",
                  (light, temperature, water, battery))
        conn.commit()
        print("Database written")
    finally:
        conn.close()