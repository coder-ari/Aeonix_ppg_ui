from bluepy.btle import Scanner, Peripheral, UUID, DefaultDelegate, BTLEException
import json
import time

class NotificationDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Notification from handle {cHandle}: {data.decode('utf-8')}")

def scan_for_devices():
    scanner = Scanner()
    devices = scanner.scan(10.0)
    for dev in devices:
        print(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
        for (adtype, desc, value) in dev.getScanData():
            print(f"  {desc} = {value}")
    return devices

def connect_to_device(device_address, service_uuid, write_char_uuid, read_char_uuid):
    print(f"Connecting to device with address: {device_address}")
    peripheral = Peripheral(device_address)
    peripheral.setDelegate(NotificationDelegate())

    # Get service
    service = peripheral.getServiceByUUID(UUID(service_uuid))
    if not service:
        raise Exception(f"Service with UUID {service_uuid} not found.")

    # Get characteristics
    write_char = service.getCharacteristics(UUID(write_char_uuid))
    if not write_char:
        raise Exception(f"Write characteristic with UUID {write_char_uuid} not found.")
    write_char = write_char[0]

    read_char = service.getCharacteristics(UUID(read_char_uuid))
    if not read_char:
        raise Exception(f"Read characteristic with UUID {read_char_uuid} not found.")
    read_char = read_char[0]

    return peripheral, write_char, read_char

def write_json_to_characteristic(characteristic, data):
    json_data = json.dumps(data)
    characteristic.write(json_data.encode('utf-8'), withResponse=True)
    print(f"Successfully written data to characteristic: {json_data}")

def enable_notifications(peripheral, characteristic):
    try:
        cccid = characteristic.getHandle() + 1
        peripheral.writeCharacteristic(cccid, b'\x01\x00', True)
        print(f"Enabled notifications for characteristic: {characteristic.uuid}")
    except BTLEException as e:
        print(f"Failed to enable notifications: {e}")

def read_from_characteristic(peripheral):
    while True:
        if peripheral.waitForNotifications(1.0):
            continue
        print("Waiting for notification...")

if __name__ == "__main__":
    json_data_to_send = {
        "SamplingRate": 1000,
        "Brightness": 30,
        "SampleAverage":1,
        "LedMode":1,
        "PulseWidth":411,
        "AdcRange":16384
    }
    DEVICE_ADDRESS = "30:30:f9:18:19:09"  
    SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" 
    WRITE_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  
    READ_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

    try:
        print("Scanning for devices...")
        devices = scan_for_devices()
        
        if not any(dev.addr == DEVICE_ADDRESS for dev in devices):
            raise Exception(f"Device with address {DEVICE_ADDRESS} not found during scan.")
        
        peripheral, write_char, read_char = connect_to_device(DEVICE_ADDRESS, SERVICE_UUID, WRITE_CHAR_UUID, READ_CHAR_UUID)
        write_json_to_characteristic(write_char, json_data_to_send)
        enable_notifications(peripheral, read_char)
        read_from_characteristic(peripheral)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            peripheral.disconnect()
            print("Disconnected from device.")
        except:
            pass
