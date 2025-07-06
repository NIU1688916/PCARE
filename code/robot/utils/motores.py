import time
from ..communication.arduino_connection import ArduinoNano

motor1 = 1
motor2 = 2
DISTANCIA_SEGURIDAD = 15  # cm

def conversion(distancia, velocidad):
    """
    Convierte la distancia y velocidad a un tiempo de espera.
    :param distancia: Distancia a recorrer.
    :param velocidad: Velocidad del robot.
    :return: Tiempo de espera en segundos.
    """
    # Ajustar según el radio o pasos del motor
    factor_rueda = 1.0  # Factor de conversión para la rueda
    tiempo_espera = distancia / velocidad*factor_rueda
    return tiempo_espera

def activar_bomba_agua():
    #Esto deberia llamar a la funcion de arduino connection y llamar a la funcion de activar bomba de agua
    #Esperar X segundos (Hay que calcular cuanto agua necessita)
    ArduinoNano.bomba_agua(1) #El parametro es el tiempo que la bomba estara encendida
    
def avanzar(distancia, velocidad=100):
    adelante = true
    ArduinoNano.avanzar(adelante)
    return True  # Avance completado
    
def retroceder(distancia, velocidad=100):
    adelante = false
    ArduinoNano.avanzar(adelante)
    return True  # Completado

def girar(orientacion_actual, nueva_orientacion, velocidad=100):
    """
    Gira el robot desde la orientación actual hacia la nueva orientación.
    Usa los motores para realizar el giro correcto.
    """
    ArduinoNano.girar()
