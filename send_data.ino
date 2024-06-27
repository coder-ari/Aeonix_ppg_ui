#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

BLEServer* pServer = nullptr;
BLECharacteristic* notifyCharacteristic = nullptr;
BLECharacteristic* readCharacteristic = nullptr;
bool deviceConnected = false;
bool startSending = false;
const int payloadSize = 20; // Adjust the size as needed
char payload[payloadSize];

const char* serviceUUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
const char* notifyCharacteristicUUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
const char* readCharacteristicUUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
  }
};

class ReadCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String value = pCharacteristic->getValue().c_str();

    if (value.length() > 0) {
      DynamicJsonDocument doc(200);
      DeserializationError error = deserializeJson(doc, value);
      
      if (!error) {
        // Assume JSON contains a key "start" to trigger data sending
        if (doc.containsKey("start")) {
          startSending = doc["start"];
        }
      }
    }
  }
};

void setup() {
  Serial.begin(115200);

  BLEDevice::init("ESP32");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService* pService = pServer->createService(serviceUUID);

  notifyCharacteristic = pService->createCharacteristic(
                           notifyCharacteristicUUID,
                           BLECharacteristic::PROPERTY_NOTIFY
                         );

  notifyCharacteristic->addDescriptor(new BLE2902());

  readCharacteristic = pService->createCharacteristic(
                         readCharacteristicUUID,
                         BLECharacteristic::PROPERTY_WRITE
                       );

  readCharacteristic->addDescriptor(new BLE2902());
  readCharacteristic->setCallbacks(new ReadCallbacks());

  pService->start();

  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(serviceUUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Waiting for a client connection to notify...");
}

void loop() {
  if (deviceConnected && startSending) {
    for (int i = 0; i < payloadSize; i++) {
      payload[i] = random(0, 256); // Generate random data
    }
    notifyCharacteristic->setValue((uint8_t*)payload, payloadSize);
    notifyCharacteristic->notify();
    delay(1000); // Adjust the delay as needed
  }
}
