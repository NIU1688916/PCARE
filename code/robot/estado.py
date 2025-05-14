import subprocess
import threading
import time
import communication.arduino_connection as Arduino
from utils.motores import activar_bomba_agua
import matplotlib.pyplot as plt
import numpy as np
import os
from utils.navigation import Navigation
from vision.mapeo import ORBSLAM2Mapper
import config
class Planta:
    def __init__(self, nombre, humedad_opt, luz_opt):
        self.nombre = nombre
        self.humedad_opt = humedad_opt
        self.luz_min = luz_opt

class Lecturas:
    def __init__(self):
        self.humedad = 0
        self.luz = 0
        self.wifi = 0
        self.arduino = Arduino.ArduinoNano(port=config.PUERTO_ARDUINO)  # Inicializa la conexión con el Arduino


    def get_lecturas(self):
        """
        Devuelve las lecturas de humedad, luz e intensidad WiFi.
        :return: Tupla con las lecturas (humedad, luz, wifi).
        """
        return self.humedad, self.luz, self.wifi

    def obtener_intensidad_wifi(self):
        """
        Obtiene la intensidad de la señal WiFi usando el comando `iwconfig`.
        :return: Intensidad de la señal WiFi como cadena, o None si ocurre un error.
        """
        try:
            result = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT, universal_newlines=True)
            for line in result.split('\n'):
                if 'Signal level' in line:
                    # Extraer el nivel de señal
                    parts = line.split('Signal level=')
                    if len(parts) > 1:
                        valor = parts[1].split(' ')[0]  # Extraer el valor de la señal
                        self.wifi = valor
                        return valor  # Devuelve el valor de la señal
            return "No se pudo obtener la intensidad de la señal"
        except Exception as e:
            return f"Error al obtener la intensidad de la señal: {str(e)}"
    
    def tomar_lecturas(self):
        # Aquí iría el código para tomar las lecturas de los sensores
        humedad = self.arduino.read_sensor("SENSOR:HUMEDAD")
        luminocidad = self.arduino.read_sensor("SENSOR:LUZ")
        intensidad_wifi = self.obtener_intensidad_wifi()
        self.humedad = humedad
        self.luz = luminocidad  
        return humedad, luminocidad, intensidad_wifi

class Celda:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lecturas = Lecturas()
        self.es_base = False
        self.es_obstaculo = False


    def get_posicion(self):
        """
        Devuelve la posición de la celda.
        :return: Tupla con las coordenadas (x, y).
        """
        return self.x, self.y
    def tomar_lecturas(self):
        self.lecturas.tomar_lecturas()

class EstadoRobot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EstadoRobot, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.celdas = []
        self.celda_actual = None
        self.planta = None
        self.modo = "Exploracion" #Modo auto 
        self.mapa_habitacion = []
        self.base = (0, 0) # Coordenadas de la base
        self.navigation = Navigation(self)  # Instancia de la clase Navigation
        self.monitor_ambiente_thread = None
        self.orbslam2 = ORBSLAM2Mapper(camera_params_path="camera_params.yaml", camera_index=0, resolution=(640, 480), framerate=30) #Esto hay que verificar si los datos estan bien

    def set_planta(self, planta):
        """
        Establece la planta a cuidar.
        :param planta: Objeto Planta que contiene la información de la planta.
        """
        self.planta = planta
        print(f"Planta configurada: {planta.nombre}")



    def explorar_habitacion(self):
        """
        Explora la habitación y registra las celdas.
        """
        self.navigation.explorar()
        #TODO: Implementar la logica para explorar la habitacio


    def mapear_habitacion(self):
        """
        Mapea la habitación con SLAM
        """
        self.mapa_habitacion = self.orbslam2.generar_mapeo_habitacion()
        #TODO: Implementar la logica para mapear la habitacion
        pass

    def iniciar_exploracion(self):
        self.mapear_habitacion()
        self.explorar_habitacion()
        self.cambiar_modo("Luz") # Para encontrar la luz optima

    def generar_mapa_actual(self):
        #TODO: Implementar la logica para generar el mapa actual del SLAM como lo ve el robot
        pass

    def generar_mapa_wifi(self):
        """
        Genera un mapa 2D de calor de la intensidad de la señal WiFi en la habitación.
        Guarda el mapa como una imagen en la carpeta 'data' con el nombre 'mapa_wifi.png'.
        """

        # Verificar que hay celdas con datos
        if not self.celdas:
            print("No hay celdas registradas para generar el mapa.")
            return

        # Extraer coordenadas y valores de intensidad WiFi
        x_coords = []
        y_coords = []
        wifi_intensities = []

        for celda in self.celdas:
            x_coords.append(celda.x)
            y_coords.append(celda.y)
            _, _, intensidad = celda.lecturas.get_lecturas()
            try:
                wifi_intensities.append(float(intensidad))
            except ValueError:
                wifi_intensities.append(0)  # Valor por defecto si no se puede convertir

        # Crear un gráfico 2D de calor
        plt.figure()
        plt.scatter(x_coords, y_coords, c=wifi_intensities, cmap='viridis', marker='o')
        plt.colorbar(label='Intensidad WiFi')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Mapa de Intensidad WiFi')

        # Crear la carpeta 'data' si no existe
        os.makedirs('data', exist_ok=True)

        # Guardar el gráfico como imagen
        file_path = os.path.join('data', 'mapa_wifi.png')
        plt.savefig(file_path)
        plt.close()

        print(f"Mapa de intensidad WiFi guardado en: {file_path}")
        
        # Retornar la ruta de la imagen generada
        return file_path

    def monitor_ambiente(self, varianza=0.1):
            while self.modo == "Standby":
                if self.planta and self.celda_actual:
                    humedad_actual, luz_actual, _ = self.celda_actual.lecturas.tomar_lecturas()
                    humedad_objetivo = self.planta.humedad_opt
                    luz_objetivo = self.planta.luz_min
                    if not ((1-varianza) * humedad_objetivo <= humedad_actual <= (1+varianza) * humedad_objetivo):
                        print("Advertencia: La humedad está fuera del rango objetivo.")
                        self.cambiar_modo("Riego")
                        self.monitor_ambiente_thread.join()  # Unir el thread al principal

                    if not ((1-varianza) * luz_objetivo <= luz_actual <= (1+varianza) * luz_objetivo):
                        print("Advertencia: La luz está fuera del rango objetivo.")
                        self.cambiar_modo("Luz")
                        self.monitor_ambiente_thread.join()  # Unir el thread al principal

                time.sleep(600)  # Esperar 10 minutos
    def cambiar_modo(self, nuevo_modo):
        """
        Cambia el modo de operación del robot.
        :param nuevo_modo: Nuevo modo a establecer (e.g., "Exploracion", "Standby").
        """
        self.modo = nuevo_modo
        if nuevo_modo == "Standby":
            self.monitor_ambiente_thread = threading.Thread(target=self.monitor_ambiente)
            self.monitor_ambiente_thread.start()
        elif nuevo_modo == "Riego":
            activar_bomba_agua()
            humedad_actual, _, _ = self.celda_actual.lecturas.tomar_lecturas()
            if humedad_actual >= self.planta.humedad_opt:
                print("La planta ha sido regada correctamente.")
                self.cambiar_modo(self, "Standby")
            else:
                print("Error: La planta no ha sido regada correctamente.")
                self.cambiar_modo(self, "base")
        elif nuevo_modo == "Luz":
            #TODO: Implementar la logica para encontrar la celda con la luz optima
            self.cambiar_modo("Standby")
            pass
        elif nuevo_modo == "base":
            self.navigation.go_to(self.celda_actual.get_posicion() ,self.base)
            #TODO: Implementar el detector aruco para orientarse a la base
            self.navigation.orientate_to_base(self.base, aruco_detector, camera)
            #TODO: Implementar la logica para acercarse a la base
            tiempo_espera = 5  # Tiempo de espera en segundos para cargar el agua
            time.sleep(tiempo_espera)
            self.cambiar_modo("Exploracion")
        elif nuevo_modo == "Exploracion":
            #Este modo se encarga de explorar la habitacion
            self.iniciar_exploracion(self)




    def nueva_celda(self, x, y):
        #Esto se encarga de crear una nueva celda y registrar los datos
        celda = Celda(x, y)
        celda.tomar_lecturas()
        self.celda_actual = celda
        self.celdas.append(celda)
        return celda
