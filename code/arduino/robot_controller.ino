#include <Servo.h>

// Lectura de sensor de humedad en A1 y fotoresistor en A0
const int HUMEDAD_PIN = A1;   // Sensor de humedad del suelo
const int LUZ_PIN     = A0;   // Fotoresistor (sensor de luz)

const float ADC_MAX = 1023.0;


// Pines de control
const int ENA = 5;  // PWM izquierdo
const int IN1 = 2;
const int IN2 = 3;

const int ENB = 9; // PWM derecho
const int IN3 = 4;
const int IN4 = 6;

const int ENA_BOMBA = 10;
const int IN1_BOMBA = 7;
const int IN2_BOMBA = 11;

const int trigPin = 12;
const int echoPin = 13;

void setup() {
  
  pinMode(HUMEDAD_PIN, INPUT); // No es estrictamente necesario, pero da claridad
  pinMode(LUZ_PIN, INPUT);
    // Pines como salida
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(ENA_BOMBA, OUTPUT);
  pinMode(IN1_BOMBA, OUTPUT);
  pinMode(IN2_BOMBA, OUTPUT);

  // Bomba OFF al iniciar
  analogWrite(ENA_BOMBA, 0);
  digitalWrite(IN1_BOMBA, LOW);
  digitalWrite(IN2_BOMBA, LOW);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}
long leerDistanciaCM() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duracion = pulseIn(echoPin, HIGH, 30000); // 30ms timeout (~500cm)

  if (duracion == 0) {
    return -1; // Indica que no se recibió eco
  }

  long distancia = duracion * 0.034 / 2;
  return distancia;
}


// Función para mover el robot
void mover(int velocidadIzq, int velocidadDer, bool adelante) {
  if (adelante) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }

  analogWrite(ENA, velocidadIzq);
  analogWrite(ENB, velocidadDer);
}


// Girar sobre el eje (giro en el sitio)
void girar90(bool derecha) {
  if (derecha) {
    // Lado izquierdo adelante, derecho atrás
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  } else {
    // Lado izquierdo atrás, derecho adelante
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }

  // Velocidad (ajusta según tu robot)
  analogWrite(ENA, 100);
  analogWrite(ENB, 150);

  // Tiempo necesario para girar 90°
  delay(2400);  // ← AJUSTA este valor tras pruebas

  // Detener motores
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void bomba(delay){
  digitalWrite(IN1_BOMBA, HIGH);
  digitalWrite(IN2_BOMBA, LOW);
  analogWrite(ENA_BOMBA, 255);   
  delay(2000);
  analogWrite(ENA_BOMBA, 0);
  digitalWrite(IN1_BOMBA, LOW);
  digitalWrite(IN2_BOMBA, LOW);

}


void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Eliminar espacios en blanco o saltos de línea

if (cmd.startsWith("MOTOR:")) {
  if (cmd.startsWith("MOTOR:GIRAR:")) {
    String direccion = cmd.substring(12); // Después de "MOTOR:GIRAR:"
    bool derecha = direccion.equalsIgnoreCase("Derecha");
    girar90(derecha)
    }

  } else if (cmd.startsWith("MOTOR:MOVER:")) {
    int index1 = cmd.indexOf(':', 12); // posición del primer valor (VElizq)
    int index2 = cmd.indexOf(':', index1 + 1); // VElder
    int index3 = cmd.indexOf(':', index2 + 1); // Adelante

    if (index1 != -1 && index2 != -1 && index3 != -1) {
      int velIzq = cmd.substring(12, index1).toInt();
      int velDer = cmd.substring(index1 + 1, index2).toInt();
      String direccionStr = cmd.substring(index2 + 1);
      direccionStr.trim();
      direccionStr.toLowerCase();
      bool adelante = (direccionStr == "true");
      mover(velIzq, velDer, adelante)
    }
  }
}
 else if (cmd.startsWith("BOMBA:")) {
      int delay = cmd.substring(6).toInt();
      bomba(delay)
    } else if (cmd.startsWith("SENSOR:")) {
      String sensor = cmd.substring(7);
      if (sensor == "HUMEDAD") {
        int humedad = analogRead(sensorHumedad);
        float humedadPct = (humedad / ADC_MAX) * 100.0;
        Serial.print("HUMEDAD:"); Serial.println(humedadPct);
      } else if (sensor == "LUZ") {
        int valorLuz     = analogRead(LUZ_PIN);
        float luzPct     = (valorLuz     / ADC_MAX) * 100.0;
        Serial.print("LUZ:"); Serial.println(luzPct);
      } else if (sensor == "DISTANCIA") {
        float dist = leerDistanciaCM()
        Serial.print("DISTANCIA:"); Serial.println(dist);
      } else {
        Serial.println("SENSOR:NO_VALIDO");
      }
    }
  }
}
