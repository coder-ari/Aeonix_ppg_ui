#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>

BLECharacteristic *pCharacteristic;
BLEAdvertising *pAdvertising;
bool deviceConnected = false;
bool oldDeviceConnected = false;
String jsonPayload = "{\"key\":\"value\"}";

class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    }

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      pAdvertising->start(); // Restart advertising on disconnect
      Serial.println("Restart advertising");
    }
};

void setup() {
  Serial.begin(115200);

  BLEDevice::init("ESP32_BLE");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(BLEUUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e"));

  pCharacteristic = pService->createCharacteristic(
                      BLEUUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e"),
                      BLECharacteristic::PROPERTY_WRITE |
                      BLECharacteristic::PROPERTY_WRITE_NR
                    );

  BLECharacteristic *pCharacteristicNotify = pService->createCharacteristic(
                      BLEUUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e"),
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  pCharacteristicNotify->addDescriptor(new BLE2902());

  pService->start();

  pAdvertising = pServer->getAdvertising(); // Assign advertising globally
  pAdvertising->start();

  Serial.println("Waiting for a BLE connection...");
}

void loop() {
  if (deviceConnected) {
    pCharacteristic->setValue((uint8_t*)jsonPayload.c_str(), jsonPayload.length());
    pCharacteristic->notify();

    delay(1000); // Adjust delay as needed for your application
  }

  delay(20); // Allow some delay in the loop for BLE processing
}
