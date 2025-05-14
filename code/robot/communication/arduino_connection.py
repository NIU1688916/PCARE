import serial
import time

class ArduinoNano:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ArduinoNano, cls).__new__(cls)
        return cls._instance

    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Inicializa la conexión serial con el Arduino Nano.
        :param port: Puerto serial donde está conectado el Arduino (e.g., '/dev/ttyUSB0').
        :param baud_rate: Velocidad de comunicación serial (por defecto: 9600).
        :param timeout: Tiempo de espera para la comunicación serial (en segundos).
        """
        if not hasattr(self, 'initialized'):  # Evitar re-inicialización
            self.port = port
            self.baud_rate = baud_rate
            self.timeout = timeout
            self.serial_connection = None
            self.initialized = True
            self.connect()

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

    def mover_motor(self, motor, valor, velocidad=10):
                """
                Envía un comando al Arduino Nano para mover un motor específico.
                :param motor: Identificador del motor (e.g., 'MOTOR1').
                :param valor: Valor para controlar el motor (e.g., velocidad o posición).
                """
                if not self.serial_connection or not self.serial_connection.is_open:
                    print("La conexión serial no está abierta.")
                    return
                try:
                    command = f"MOTOR:{motor}:{valor}\n"
                    self.serial_connection.write(command.encode())  # Enviar comando
                    print(f"Comando enviado: {command.strip()}")
                except serial.SerialException as e:
                    print(f"Error al enviar comando al motor: {e}")

    def bomba_agua(self, valor):
        """
        Envía un comando al Arduino Nano para controlar la bomba de agua.
        Activa la bomba con 1, espera el tiempo especificado en valor, y luego la apaga.
        :param valor: Tiempo en segundos que la bomba estará encendida.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            print("La conexión serial no está abierta.")
            return
        try:
            # Encender la bomba
            command_on = "BOMBA:1\n"
            self.serial_connection.write(command_on.encode())
            print(f"Comando enviado: {command_on.strip()}")
            
            # Esperar el tiempo especificado
            time.sleep(valor)
            
            # Apagar la bomba
            command_off = "BOMBA:0\n"
            self.serial_connection.write(command_off.encode())
            print(f"Comando enviado: {command_off.strip()}")
        except serial.SerialException as e:
            print(f"Error al controlar la bomba de agua: {e}")


# Ejemplo de uso:
if __name__ == "__main__":
    arduino = ArduinoNano(port='/dev/ttyUSB0') 

    # Leer el sensor de humedad
    humedad = arduino.read_sensor("SENSOR:HUMEDAD")
    print(f"Humedad: {humedad}")

    # Leer el sensor de luz
    luz = arduino.read_sensor("SENSOR:LUZ")
    print(f"Luz: {luz}")

    # Leer el sensor de distancia
    distancia = arduino.read_sensor("SENSOR:DISTANCIA")
    print(f"Distancia: {distancia}")