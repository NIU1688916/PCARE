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
    tiempo_total = conversion(distancia, velocidad)
    tiempo_paso = 0.2  # ajustar: cuanto avanza cada paso corto
    pasos = int(tiempo_total / tiempo_paso)

    for _ in range(pasos):
        # Leer distancia
        distancia_objeto = ArduinoNano.leer_ultrasonico()
        if distancia_objeto is not None and distancia_objeto < DISTANCIA_SEGURIDAD:
            print("Obstáculo detectado. Parando.")
            ArduinoNano.mover_motor(motor1, 0, 0)
            ArduinoNano.mover_motor(motor2, 0, 0)
            return False  # Indica que no se pudo avanzar

        # Avanzar un paso corto
        ArduinoNano.mover_motor(motor1, 1, velocidad)
        ArduinoNano.mover_motor(motor2, 1, velocidad)
        time.sleep(tiempo_paso)

    # Detener motores al final
    ArduinoNano.mover_motor(motor1, 0, 0)
    ArduinoNano.mover_motor(motor2, 0, 0)
    return True  # Avance completado


    time.sleep(tiempo_espera)  # Esperar el tiempo calculado
    # Detener el motor
    ArduinoNano.mover_motor(motor1,0,velocidad) 
    ArduinoNano.mover_motor(motor2,0,velocidad) 
    
def retroceder(distancia, velocidad=100):
    tiempo_espera = conversion(distancia, velocidad)
    ArduinoNano.mover_motor(motor1, -1, velocidad)
    ArduinoNano.mover_motor(motor2, -1, velocidad)
    time.sleep(tiempo_espera)
    ArduinoNano.mover_motor(motor1, 0, 0)
    ArduinoNano.mover_motor(motor2, 0, 0)

def girar(orientacion_actual, nueva_orientacion, velocidad=100):
    """
    Gira el robot desde la orientación actual hacia la nueva orientación.
    Usa los motores para realizar el giro correcto.
    """
    # Calcular diferencia (mod 4 para evitar números negativos)
    diferencia = (nueva_orientacion - orientacion_actual) % 4

    # Duración estimada para girar 90 grados (ajustar con pruebas reales)
    duracion_90 = 0.5

    if diferencia == 0:
        # No hace falta girar
        return
    elif diferencia == 1:
        # Giro a la derecha 90°
        ArduinoNano.mover_motor(motor1, 1, velocidad)
        ArduinoNano.mover_motor(motor2, -1, velocidad)
        time.sleep(duracion_90)
    elif diferencia == 3:
        # Giro a la izquierda 90°
        ArduinoNano.mover_motor(motor1, -1, velocidad)
        ArduinoNano.mover_motor(motor2, 1, velocidad)
        time.sleep(duracion_90)
    elif diferencia == 2:
        # Giro 180°
        ArduinoNano.mover_motor(motor1, 1, velocidad)
        ArduinoNano.mover_motor(motor2, -1, velocidad)
        time.sleep(duracion_90 * 2)

    # Detener motores
    ArduinoNano.mover_motor(motor1, 0, 0)
    ArduinoNano.mover_motor(motor2, 0, 0)
