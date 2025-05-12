from estado import robot_estado
from motores import activar_bomba_agua 

def evaluar_posicion():
    l = robot_estado.lecturas
    p = robot_estado.planta
    return l.humedad < p.humedad_opt and l.luz >= p.luz_min

def ciclo_robot():
    if evaluar_posicion():
        activar_bomba_agua(robot_estado.planta.tiempo_riego)
    else:
        print("Buscando mejor posición...")
        
    