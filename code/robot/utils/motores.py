import time
from ..communication.arduino_connection import ArduinoNano

def activar_bomba_agua():
    #Esto deberia llamar a la funcion de arduino connection y llamar a la funcion de activar bomba de agua
    #Esperar X segundos (Hay que calcular cuanto agua necessita)
    ArduinoNano.bomba_agua(1)
    #time.sleep(X)
    ArduinoNano.bomba_agua(0) 
    
def avanzar(tiempo, velocidad):
    ArduinoNano.mover_motor() #Hay que mirar de que avanze
    pass
    
def retroceder(tiempo, velocidad):
    ArduinoNano.mover_motor() #Hay que mirar de que avanze
    pass

def girar(grados):
    pass

