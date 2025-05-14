import time
from ..communication.arduino_connection import ArduinoNano



def conversion(distancia, velocidad):
    """
    Convierte la distancia y velocidad a un tiempo de espera.
    :param distancia: Distancia a recorrer.
    :param velocidad: Velocidad del robot.
    :return: Tiempo de espera en segundos.
    """
    factor_rueda = 1.0  # Factor de conversión para la rueda
    tiempo_espera = distancia / velocidad*factor_rueda
    return tiempo_espera




def activar_bomba_agua():
    #Esto deberia llamar a la funcion de arduino connection y llamar a la funcion de activar bomba de agua
    #Esperar X segundos (Hay que calcular cuanto agua necessita)
    ArduinoNano.bomba_agua(1) #El parametro es el tiempo que la bomba estara encendida
    
def avanzar(distancia, velocidad=10):
    tiempo_espera = conversion(distancia, velocidad)
    #Activar el motor para avanzar
    ArduinoNano.mover_motor(motor1,1,velocidad) 
    ArduinoNano.mover_motor(motor2,1,velocidad) 


    time.sleep(tiempo_espera)  # Esperar el tiempo calculado
    # Detener el motor
    ArduinoNano.mover_motor(motor1,0,velocidad) 
    ArduinoNano.mover_motor(motor2,0,velocidad) 
    pass
    
def retroceder(distancia, velocidad=10):
    ArduinoNano.mover_motor() #Hay que mirar de que retroceda
    pass

def girar(grados, direccion="izquierda", velocidad=10):
    ArduinoNano.mover_motor() #Hay que mirar de que gire
    pass

