from motores import avanzar, retroceder,girar
import math
from frontier import detect_frontiers, get_closest_frontier
class Navigation:
    def __init__(self, estado_robot):
        """
        Inicializa la clase Navigation.
        """
        self.estado_robot = estado_robot
        pass

    def go_to(self, posicion_original, posicion_destino):
        """
        Mueve el robot a la posición (x, y) en el mapa.
        """
        xfinal = posicion_destino[0]
        yfinal = posicion_destino[1]
        xactual = posicion_original[0]
        yactual = posicion_original[1]


        #Codigo para mover el robot
        #TODO: Implementar la logica para mover el robot
        self.estado_robot.nueva_celda(xfinal, yfinal)

        pass

    def orientate_to_base(self, posicion_base, aruco_detector, camera):
        """
        Orienta el robot hacia la base utilizando un marcador ArUco.
        :param posicion_base: Posición de la base (x, y).
        :param aruco_detector: Detector de marcadores ArUco.
        :param camera: Cámara para capturar imágenes.
        """
        while True:
            # Capturar una imagen de la cámara
            frame = camera.read()
            
            # Detectar marcadores ArUco en la imagen
            corners, ids, _ = aruco_detector.detectMarkers(frame)
            
            if ids is not None and len(ids) > 0:
                # Suponiendo que el marcador de la base tiene un ID específico
                base_marker_id = 1
                if base_marker_id in ids:
                    # Obtener la posición del marcador de la base
                    index = list(ids).index(base_marker_id)
                    marker_corners = corners[index]
                    
                    # Calcular el ángulo de orientación hacia el marcador
                    center_x = (marker_corners[0][0][0] + marker_corners[0][2][0]) / 2
                    frame_center_x = frame.shape[1] / 2
                    
                    if abs(center_x - frame_center_x) < 10:  # Tolerancia de alineación
                        print("Robot orientado hacia la base.")
                        break
                    elif center_x < frame_center_x:
                        girar(-5, direccion="left")  # Girar a la izquierda
                    else:
                        girar(5, direccion="rigth")  # Girar a la derecha
            else:
                print("Marcador de la base no detectado. Ajustando...")
                girar(5)  # Girar para buscar el marcador

    def explorar(self):
        """
        Explora la habitación utilizando el sistema de navegación de frontier y el mapa.
        """
        pass