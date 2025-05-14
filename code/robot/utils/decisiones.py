from estado import EstadoRobot
from communication.app_interface import RobotServer


def ciclo_robot():
    estado = EstadoRobot()
    server = RobotServer(estado)
    server.run_in_thread()
    estado.iniciar_exploracion()
        
    