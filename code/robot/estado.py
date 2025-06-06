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
from utils.frontier import detect_frontiers, get_closest_frontier
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
    def __init__(self, x, y,es_base=False):
        self.x = x
        self.y = y
        self.lecturas = Lecturas()
        self.es_base = False
        self.es_obstaculo = False
        self.visitada = False

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
        self.planta = Planta("Menta", humedad_opt=60, luz_opt=200)  # Planta de ejemplo
        self.modo = "Exploracion" #Modo auto 
        self.base = (0, 0) # Coordenadas de la base
        self.navigation = Navigation(self)  # Instancia de la clase Navigation
        self.monitor_ambiente_thread = None
        self.orbslam2 = ORBSLAM2Mapper()

        self.posicion = (0, 0)  # (x, y). Se actualiza con cada movimiento del robot
        self.orientacion = 0  # 0=norte, 1=este, 2=sur, 3=oeste
        self.tamaño_mapa = 100
        self.mapa = np.full((self.tamaño_mapa, self.tamaño_mapa), None)  # -1 = desconocido, 0 = libre, 1 = visitado
        self.luz_map = np.zeros((self.tamaño_mapa, self.tamaño_mapa))
        self.historial_luz = {}  # (x, y) → [lecturas]
        
        celda_base = Celda(0, 0, es_base=True)
        celda_base.visitada = True
        self.mapa[0][0] = celda_base

        self.agua_restante = 100
        self.exploracionFinalizada = False



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



    def iniciar_exploracion(self):
        
        while not self.exploracionFinalizada :
            fronteras = detect_frontiers(self.mapa)
            if not fronteras:
                print("No quedan zonas por explorar")
                self.exploracionFinalizada = True
                break

            # 2. Elegir frontera más cercana
            objetivo = get_closest_frontier(fronteras, self.posicion)
            if not objetivo:
                break

            # 3. Ir hasta la frontera con A*
            print(f"🧭 Navegando hacia {objetivo}")
            x,y,theta = self.orbslam2.obtener_posicion_2d_xy(self) #Posicion actual del robot
            self.nueva_celda(x, y)
            exito = self.navigation.go_to((x, y), objetivo)
            if not exito:
                print(f"No se pudo llegar a {objetivo}")
                continue

            # 4. Tomar lectura y actualizar mapa
            self.mapa[x][y].tomar_lecturas()
            

    def actualizar_lecturas(self):
        humedad, luz, _ = self.lecturas.get_lecturas()
        self.mapa[self.x][self.y] = 0  # zona libre
        self.luz_map[self.x][self.y] = luz
        self.historial_luz.setdefault((self.x, self.y), []).append((time.time(), luz))

        if humedad < self.planta.humedad_opt:
            activar_bomba_agua()

    def generar_mapa_actual(self):
        return self.orbslam2.exportar_mapa_png()

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
    def encontrar_luz_optima(self):
        """
        Busca la celda visitada cuya lectura de luz esté más cerca del valor óptimo de la planta.
        Devuelve la posición (x, y) de esa celda.
        """
        luz_objetivo = self.planta.luz_min
        mejor_celda = None
        mejor_diferencia = float('inf')

        for x in range(self.tamaño_mapa):
            for y in range(self.tamaño_mapa):
                celda = self.mapa[x][y]
                if celda and celda.visitada:
                    luz = celda.lecturas.luz
                    diferencia = abs(luz - luz_objetivo)
                    if diferencia < mejor_diferencia:
                        mejor_diferencia = diferencia
                        mejor_celda = celda

        if mejor_celda:
            return mejor_celda.get_posicion()
        else:
            return self.base  # Si no hay celdas visitadas, vuelve a la base
    
    def cargar_agua(self):
        #Funcion que una vez ha ido a la base (Hecho antes de llamarla) se orienta, 
        self.navigation.posicionarse_agua()
        activar_bomba_agua()
        self.agua_restante -= 1
        time.sleep(2)  # Simula el tiempo de riego TODO: Mirar cuando tiempo hay que esperar
        
    
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
            posicion_luz_destino = self.encontrar_luz_optima()
            self.navigation.go_to(self.celda_actual.get_posicion() ,posicion_luz_destino)
            self.cambiar_modo("Standby")
            pass
        elif nuevo_modo == "base":
            self.navigation.volver_a_base()
            self.cargar_agua()
            self.cambiar_modo("Exploracion")
        elif nuevo_modo == "Exploracion":
            #Este modo se encarga de explorar la habitacion
            self.iniciar_exploracion(self)
            self.cambiar_modo("Standby")

    def nueva_celda(self, x, y):
        """ #Esto se encarga de crear una nueva celda y registrar los datos
        celda = Celda(x, y)
        celda.tomar_lecturas()
        self.celda_actual = celda
        self.celdas.append(celda)
        return celda """

        """
        Actualiza la posición del robot y marca la celda como visitada.
        """
        
        if self.mapa[x][y] is None:
            self.mapa[x][y] = Celda(x, y)
        
        self.mapa[x][y].visitada = True
