import serial
import time

class ArduinoNano:
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Inicializa la conexión serial con el Arduino Nano.
        :param port: Puerto serial donde está conectado el Arduino (e.g., '/dev/ttyUSB0').
        :param baud_rate: Velocidad de comunicación serial (por defecto: 9600).
        :param timeout: Tiempo de espera para la comunicación serial (en segundos).
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        """Establece la conexión serial con el Arduino Nano."""
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Esperar a que la conexión se estabilice
            print("Conexión establecida con el Arduino Nano.")
        except serial.SerialException as e:
            print(f"Error al conectar con el Arduino Nano: {e}")

    def disconnect(self):
        """Cierra la conexión serial."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Conexión cerrada.")

    def read_sensor(self, sensor_command):
        """
        Solicita datos de un sensor específico al Arduino Nano.
        :param sensor_command: Comando para identificar el sensor (e.g., 'SENSOR1').
        :return: Valor del sensor como cadena, o None si ocurre un error.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            print("La conexión serial no está abierta.")
            return None
        try:
            self.serial_connection.write(f"{sensor_command}\n".encode())  # Enviar comando
            data = self.serial_connection.readline().decode('utf-8').strip()  # Leer respuesta
            return data
        except serial.SerialException as e:
            print(f"Error al leer datos: {e}")
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    arduino = ArduinoNano(port='/dev/ttyUSB0') 
    arduino.connect()

    try:
        sensor1_data = arduino.read_sensor("SENSOR1")
        print(f"Sensor 1: {sensor1_data}")

        sensor2_data = arduino.read_sensor("SENSOR2")
        print(f"Sensor 2: {sensor2_data}")

        sensor3_data = arduino.read_sensor("SENSOR3")
        print(f"Sensor 3: {sensor3_data}")
    finally:
        arduino.disconnect()