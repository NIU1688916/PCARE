#Guardar en memoria
robot_estado = {
    "tipo_planta": None,
    "humedad_tierra": 0,
    "luminosidad": 0,
    "distancia_obstaculo": 0,
    "ubicacion_actual": (0, 0),
    "mapa_habitacion": [],
    "mapa_wifi": [],
    "modo_automatico": True
}

planta_config = {
    "nombre": None,
    "humedad_optima": 0,
    "riego_duracion_seg": 0,
    "luminosidad_minima": 0
}

datos_app = {
    "tipo_planta": "",
    "modo_operacion": "automatico",  # o "manual"
}
#Declaracion de funciones
#APP Mobil
def detectar_tipo_planta(imagen):
    # Supongamos una clasificación básica (mock)
    return "Cactus"

def enviar_datos_al_robot(datos):
    global datos_app
    datos_app.update(datos)

#Conexion con la app
def recibir_datos_app():
    return datos_app

def adaptar_funcionamiento_robot(datos):
    global planta_config, robot_estado
    planta_config["nombre"] = datos["tipo_planta"]
    # Ejemplo de configuración por planta
    if datos["tipo_planta"] == "Cactus":
        planta_config.update({
            "humedad_optima": 20,
            "riego_duracion_seg": 5,
            "luminosidad_minima": 200
        })
    robot_estado["modo_automatico"] = datos["modo_operacion"] == "automatico"


#Mapeo habitacion a partir de la camara
def capturar_imagen_camara():
    pass

def generar_mapeo_habitacion(imagen):
    global robot_estado
    robot_estado["mapa_habitacion"] = [[0, 0, 1], [0, 1, 0], [0, 0, 0]]


#Sensores
def leer_sensor_ultrasonido():
    return 50  # cm

def leer_sensor_luminosidad():
    return 300  # lux

def leer_sensor_humedad():
    return 25  # %

def configurar_sensores():
    global robot_estado
    robot_estado["distancia_obstaculo"] = leer_sensor_ultrasonido()
    robot_estado["luminosidad"] = leer_sensor_luminosidad()
    robot_estado["humedad_suelo"] = leer_sensor_humedad()



#Control de motores
def activar_motor_movimiento(direccion, velocidad):
    print(f"Moviendo robot hacia {direccion} con velocidad {velocidad}")

def activar_bomba_agua(tiempo):
    print(f"Activando bomba durante {tiempo} segundos")

#extra
def escanear_intensidad_wifi():
    return [[-60, -65, -70], [-55, -60, -75], [-50, -55, -60]]

def generar_mapa_calor_wifi(datos_wifi):
    global robot_estado
    robot_estado["mapa_wifi"] = datos_wifi