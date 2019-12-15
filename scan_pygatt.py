import pygatt
from datetime import datetime
from binascii import hexlify
import threading
import time

adapter = pygatt.GATTToolBackend()

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: %s" % value)
    # bytes: interval 1, voltage 2, Etotal 2, voltages 2 x 5
    interval = int.from_bytes(value[0:2], byteorder='little')
    voltage = int.from_bytes(value[2:4], byteorder='little')
    Etotal = int.from_bytes(value[4:6], byteorder='little')
    voltages = []
    for i in range(5):
        voltages.append(int.from_bytes(value[6+i*2:8+i*2], byteorder='little'))
    print(interval)
    print(voltage)
    print(Etotal)
    print(voltages)

def timer():
    time.sleep(2)

def connect():
    '''while True:
        devices = adapter.scan(run_as_root=True,timeout=10)
        print("-----------------------------------------------------------")
        for d in devices:
            print(d['address'])'''
    print("connecting ...")
    device = adapter.connect('00:00:00:00:05:19')
    print("connected!")
    now = datetime.now()
    time_of_day = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    time_of_day = time_of_day.to_bytes(4, byteorder='big')
    device.char_write(uuid = '7827089E-8794-4A57-8706-AABEC96E9E64', value=time_of_day)
    device.subscribe("30123C54-2BF8-40B3-B43D-C553E2A4A1F4",
                     callback=handle_data)
    print("subscribed!")
    thread = threading.Thread(target=timer)
    thread.start()
    thread.join()

def main():
    i = 0
    print("starting adapter...")
    adapter.start()
    while True:
        try:
            connect()
        except:
            print("error " + str(i))
            i+=1

    adapter.stop()


main()

