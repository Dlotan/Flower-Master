from bluepy.bluepy.btle import *
import struct
import sqlite3


def to_flower_uuid(hex_value):
    return UUID("%08X-84a8-11e2-afba-0002a5d5c51b" % (0x39e10000 + hex_value))


class FlowerService(object):
    def __init__(self):
        self.service = None

    def enable(self, periph):
        self.service = periph.getServiceByUUID(self.uuid)
        for characteristic in self.characteristics:
            characteristic.enable(self.service)

    def __getitem__(self, item):
        for characteristic in self.characteristics:
            if characteristic.name == item:
                return characteristic


class FlowerCharacteristic(object):
    def __init__(self):
        self.characteristic = None

    def enable(self, service):
        self.characteristic = service.getCharacteristics(self.uuid)[0]


class TimeDateCharacteristic(FlowerCharacteristic):
    name = "Date"
    uuid = to_flower_uuid(0xfd01)

    def __init__(self):
        super(TimeDateCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("<i", self.characteristic.read())[0]


class TimeService(FlowerService):
    name = "Time"
    uuid = to_flower_uuid(0xfd00)

    def __init__(self):
        super(TimeService, self).__init__()
        self.characteristics = [TimeDateCharacteristic()]


class LEDCharacteristic(FlowerCharacteristic):
    name = "LED"
    uuid = to_flower_uuid(0xfa07)

    def __init__(self):
        super(LEDCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("?", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("?", value))


class LightCharacteristic(FlowerCharacteristic):
    name = "Light"
    uuid = to_flower_uuid(0xfa01)

    def __init__(self):
        super(LightCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("<h", self.characteristic.read())[0]


class TemperatureCharacteristic(FlowerCharacteristic):
    name = "Temperature"
    uuid = to_flower_uuid(0xfa0a)

    def __init__(self):
        super(TemperatureCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class WaterCharacteristic(FlowerCharacteristic):
    name = "Water"
    uuid = to_flower_uuid(0xfa09)

    def __init__(self):
        super(WaterCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class PeriodCharacteristic(FlowerCharacteristic):
    name = "Period"
    uuid = to_flower_uuid(0xfa06)

    def __init__(self):
        super(PeriodCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("B", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("B", value))


class LiveService(FlowerService):
    name = "Live"
    uuid = to_flower_uuid(0xfa00)

    def __init__(self):
        super(LiveService, self).__init__()
        self.characteristics = [
            LEDCharacteristic(),
            LightCharacteristic(),
            TemperatureCharacteristic(),
            WaterCharacteristic(),
            PeriodCharacteristic(),
        ]


class BatteryCharacteristic(FlowerCharacteristic):
    name = "Battery"
    uuid = UUID("00002a19-0000-1000-8000-00805f9b34fb")

    def __init__(self):
        super(BatteryCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("b", self.characteristic.read())[0]


class BatteryService(FlowerService):
    name = "Battery"
    uuid = UUID("0000180f-0000-1000-8000-00805f9b34fb")

    def __init__(self):
        super(BatteryService, self).__init__()
        self.characteristics = [
            BatteryCharacteristic(),
        ]


class FlowerDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, handle, data):
        print("Notification")


class FlowerPeripheral(Peripheral):
    def __init__(self, dev_addr, addr_type):
        Peripheral.__init__(self, dev_addr, addr_type)
        self.flower_services = {
            TimeService.name: TimeService(),
            LiveService.name: LiveService(),
            BatteryService.name: BatteryService()
        }
        self.dev_addr = dev_addr
        self.addr_type = addr_type

    def print_all_connections(self):
        for service in self.getServices():
            print("-------")
            print(str(service.uuid) + " " + str(service))
            for characteristic in service.getCharacteristics():
                print("    " + str(characteristic.uuid) + " " + str(characteristic)
                      + " Handle " + str(characteristic.getHandle()))

    def make_all_connections(self):
        for service in self.getServices():
            for _ in service.getCharacteristics():
                pass

    def enable(self):
        for service in self.flower_services:
            self.flower_services[service].enable(self)

    def flower_connect(self):
        Peripheral.connect(self, self.dev_addr, self.addr_type)


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

if __name__ == '__main__':
    if not os.path.isfile(helperExe):
        raise ImportError("Cannot find required executable '%s'" % helperExe)

    flower_dev_addr = 'A0:14:3D:08:B3:51'
    flower_addr_type = ADDR_TYPE_PUBLIC
    print("Connecting to: {}, address type: {}".format(flower_dev_addr, flower_addr_type))
    conn = FlowerPeripheral(flower_dev_addr, flower_addr_type)
    print("Connection established")
    conn.setDelegate(FlowerDelegate())
    try:
        conn.make_all_connections()  # Have to make all connections at start otherwise the Battery can't connect
        conn.enable()
    finally:
        conn.disconnect()
    print("Reconnect")
    try:
        conn.flower_connect()
        conn.flower_services["Live"]["Period"].write(1)
        light = []
        temperature = []
        water = []
        for i in range(6):
            light.append(conn.flower_services["Live"]["Light"].read())
            temperature.append(conn.flower_services["Live"]["Temperature"].read())
            water.append(conn.flower_services["Live"]["Water"].read())
            print "Reading"
            time.sleep(0.5)
        conn.flower_services["Live"]["Period"].write(0)
        for meassure in (light, temperature, water):
            meassure.sort()
        insert_into_db(light[len(light)/2], temperature[len(temperature)/2], water[len(water)/2],
                       conn.flower_services["Battery"]["Battery"].read())
    finally:
        conn.disconnect()