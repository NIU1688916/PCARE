#include <Servo.h>

const int sensorHumedad = A0;
const int sensorLuz = A1;
const int trigPin = 2;
const int echoPin = 3;
const int bombaPin = 4;
const int motorIzq = 5;
const int motorDer = 6;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(bombaPin, OUTPUT);
  pinMode(motorIzq, OUTPUT);
  pinMode(motorDer, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Eliminar espacios en blanco o saltos de línea

    if (cmd.startsWith("MOTOR:")) {
      int separatorIndex = cmd.indexOf(':', 6);
      //Aqui dependiendo del motor y del valor se enciende o apaga el motor
      if (separatorIndex != -1) {
        int motor = cmd.substring(6, separatorIndex).toInt();
        int valor = cmd.substring(separatorIndex + 1).toInt();
        if (motor == 1) {
          digitalWrite(motorIzq, valor);
          digitalWrite(motorDer, valor);
        }
      }
    } else if (cmd.startsWith("BOMBA:")) {
      int valor = cmd.substring(6).toInt();
      digitalWrite(bombaPin, valor);
    } else if (cmd.startsWith("SENSOR:")) {
      String sensor = cmd.substring(7);
      if (sensor == "HUMEDAD") {
        int humedad = analogRead(sensorHumedad);
        Serial.print("HUMEDAD:"); Serial.println(humedad);
      } else if (sensor == "LUZ") {
        int luz = analogRead(sensorLuz);
        Serial.print("LUZ:"); Serial.println(luz);
      } else if (sensor == "DISTANCIA") {
        long dur, dist;
        digitalWrite(trigPin, LOW); delayMicroseconds(2);
        digitalWrite(trigPin, HIGH); delayMicroseconds(10);
        digitalWrite(trigPin, LOW);
        dur = pulseIn(echoPin, HIGH);
        dist = dur * 0.034 / 2;
        Serial.print("DISTANCIA:"); Serial.println(dist);
      } else {
        Serial.println("SENSOR:NO_VALIDO");
      }
    }
  }
}