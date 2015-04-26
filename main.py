from bluepy.bluepy.btle import *
import struct


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
            print(str(service.uuid))
            for characteristic in service.getCharacteristics():
                print("    " + str(characteristic.uuid))

    def make_all_connections(self):
        for service in self.getServices():
            for _ in service.getCharacteristics():
                pass

    def enable(self):
        for service in self.flower_services:
            self.flower_services[service].enable(self)

    def flower_connect(self):
        Peripheral.connect(self, self.dev_addr, self.addr_type)


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

        conn.flower_services["Live"]["Period"].write(1)
        for i in range(10):
            print("Light " + str(conn.flower_services["Live"]["Light"].read()))
            print("Temperature " + str(conn.flower_services["Live"]["Temperature"].read()))
            time.sleep(1)
        conn.flower_services["Live"]["Period"].write(0)
    finally:
        conn.disconnect()
    print("Reconnect")
    try:
        conn.flower_connect()
        print conn.flower_services["Battery"]["Battery"].read()
    finally:
        conn.disconnect()