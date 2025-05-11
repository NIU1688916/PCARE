#include <SoftwareSerial.h>

// Pines de los sensores
const int sensor1Pin = A0; // Sensor 1 (luz)
const int sensor2Pin = A1; // Sensor 2 (ultrasonido)
const int sensor3Pin = A2; // Sensor 3 (humedad)

void setup() {
  Serial.begin(9600); // Comunicación serial con la Raspberry Pi
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Leer comando desde la Raspberry Pi

    if (command == "SENSOR1") {
      int sensor1Value = analogRead(sensor1Pin);
      Serial.println(sensor1Value); // Enviar datos del sensor 1
    } else if (command == "SENSOR2") {
      int sensor2Value = analogRead(sensor2Pin);
      Serial.println(sensor2Value); // Enviar datos del sensor 2
    } else if (command == "SENSOR3") {
      int sensor3Value = analogRead(sensor3Pin);
      Serial.println(sensor3Value); // Enviar datos del sensor 3
    } else {
      Serial.println("UNKNOWN_COMMAND"); // Comando no reconocido
    }
  }
}