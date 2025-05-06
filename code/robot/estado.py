class Planta:
    def __init__(self, nombre, humedad_opt, luz_min, tiempo_riego):
        self.nombre = nombre
        self.humedad_opt = humedad_opt
        self.luz_min = luz_min
        self.tiempo_riego = tiempo_riego

class Lecturas:
    def __init__(self):
        self.humedad = 0
        self.luz = 0
        self.distancia = 0
        self.posicion = (0, 0)

class Celda:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.humedad = None
        self.luz = None
        self.wifi = None
        self.es_base = False
        self.es_obstaculo = False

class EstadoRobot:
    def __init__(self):
        self.lecturas = Lecturas()
        self.planta = None
        self.modo_automatico = True
        self.mapa_habitacion = []
        self.mapa_wifi = []

robot_estado = EstadoRobot()