from bluepy.bluepy.btle import *
import struct

service_list = []


class FlowerService(object):
    def __init__(self, name, short_uuid, characteristics):
        self.name = name
        self.short_uuid = short_uuid
        self.characteristics = characteristics
        self.service = None

    def __getitem__(self, item):
        for characteristic in self.characteristics:
            if characteristic.name == item:
                return characteristic


class FlowerCharacteristic(object):
    def __init__(self, name, short_uuid):
        self.name = name
        self.short_uuid = short_uuid
        self.characteristic = None


class TimeDateCharacteristic(FlowerCharacteristic):
    def __init__(self):
        super(TimeDateCharacteristic, self).__init__("Date", "fd01")

    def read(self):
        if self.characteristic:
            return struct.unpack("<i", self.characteristic.read())[0]


class TimeService(FlowerService):
    def __init__(self):
        characteristics = [TimeDateCharacteristic()]
        super(TimeService, self).__init__("Time", "fd00", characteristics)


class LEDCharacteristic(FlowerCharacteristic):
    def __init__(self):
        super(LEDCharacteristic, self).__init__("LED", "fa07")

    def read(self):
        if self.characteristic:
            return struct.unpack("?", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("?", value))


class LightCharacteristic(FlowerCharacteristic):
    def __init__(self):
        super(LightCharacteristic, self).__init__("Light", "fa01")

    def read(self):
        if self.characteristic:
            return struct.unpack("<h", self.characteristic.read())[0]


class PeriodCharacteristic(FlowerCharacteristic):
    def __init__(self):
        super(PeriodCharacteristic, self).__init__("Period", "fa06")

    def read(self):
        if self.characteristic:
            return struct.unpack("B", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("B", value))


class LiveService(FlowerService):
    def __init__(self):
        characteristics = [
            LEDCharacteristic(),
            LightCharacteristic(),
            PeriodCharacteristic(),
        ]
        super(LiveService, self).__init__("Live", "fa00", characteristics)


service_list.append(TimeService())
service_list.append(LiveService())


class FlowerDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, handle, data):
        print("Notification")


class FlowerPeripheral(Peripheral):
    def __init__(self, dev_addr, addr_type):
        self.services = {}
        self.dev_addr = dev_addr
        self.addr_type = addr_type
        Peripheral.__init__(self, dev_addr, addr_type)

    def make_long_uuids(self):
        for service in self.getServices():
            for flower_service in service_list:
                if flower_service.short_uuid in str(service.uuid):
                    flower_service.service = service
                    for characteristic in service.getCharacteristics():
                        for flower_characteristic in flower_service.characteristics:
                            if flower_characteristic.short_uuid in str(characteristic.uuid):
                                flower_characteristic.characteristic = characteristic
                                break
                    self.services[flower_service.name] = flower_service
                    break

    def flower_connect(self):
        Peripheral.connect(self, self.dev_addr, self.addr_type)


if not os.path.isfile(helperExe):
    raise ImportError("Cannot find required executable '%s'" % helperExe)

flower_dev_addr = 'A0:14:3D:08:B3:51'
flower_addr_type = ADDR_TYPE_PUBLIC
print("Connecting to: {}, address type: {}".format(flower_dev_addr, flower_addr_type))
conn = FlowerPeripheral(flower_dev_addr, flower_addr_type)
conn.setDelegate(FlowerDelegate())
try:
    conn.make_long_uuids()
    # services["Live"]["LED"].write(True)
    print("Perioud before", conn.services["Live"]["Period"].read())
    conn.services["Live"]["Period"].write(1)
    print("Perioud after", conn.services["Live"]["Period"].read())
    for i in range(30):
        print("Light", conn.services["Live"]["Light"].read())
        time.sleep(0.5)
    conn.services["Live"]["Period"].write(0)
finally:
    conn.disconnect()