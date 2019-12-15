import gatt
from datetime import datetime

DEVICE_MAC_ADDR = '00:a0:50:ce:39:6a'
SERVICE_UUID = '65994fde-e1c7-421f-92c1-86f16160b4f6'

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

        self.connect()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        print()

        self.connect()

    def services_resolved(self):
        super().services_resolved()

        data = []
        now = datetime.now()
        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            if service.uuid != SERVICE_UUID:
                continue

            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]   Characteristic [%s]" % (self.mac_address, characteristic.uuid))
                data.append(''.join([format(byte, '02x') for byte in characteristic.read_value()]))

        #print(data)
        voltage_dec = int(data[0][2:4], 16) * 256 + int(data[0][0:2], 16)
        print("%.3fV [%d]" % (float(voltage_dec) * 1.024 * 5.0 / 2048.0, voltage_dec))
        with open('log_' + str(now.strftime('%Y-%m-%d')) + '.txt', 'a') as f:
            f.write(str(now.strftime("%Y-%m-%d %H:%M:%S")) + ',')
            f.write(','.join(data))
            f.write('\n')

        self.disconnect()

    def characteristic_read_value_failed(self, characteristic, error):
        print("read value failed")

        self.disconnect()
        

print("Scanning...")

manager = gatt.DeviceManager(adapter_name='hci0')
#manager = AnyDeviceManager(adapter_name='hci0')
#manager.start_discovery()

device = AnyDevice(mac_address=DEVICE_MAC_ADDR, manager=manager)
device.connect()
manager.run()
