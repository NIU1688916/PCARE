from motores import avanzar, retroceder,girar
import math
from frontier import detect_frontiers, get_closest_frontier
import heapq  # Para la cola de prioridad en A*
import time

class Navigation:
    def __init__(self, estado_robot):
        """
        Inicializa la clase Navigation.
        """
        self.estado_robot = estado_robot

    def _heuristica(self, a, b):
        # Distancia Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _vecinos(self, nodo, mapa):
        vecinos = []
        x, y = nodo
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(mapa) and 0 <= ny < len(mapa[0]):
                if mapa[nx][ny] == 0:  # Solo celdas libres
                    vecinos.append((nx, ny))
        return vecinos
    
    def _a_star(self, mapa, inicio, objetivo):
        open_set = []
        heapq.heappush(open_set, (0, inicio))
        came_from = {}
        g_score = {inicio: 0}
        f_score = {inicio: self._heuristica(inicio, objetivo)}

        while open_set:
            _, actual = heapq.heappop(open_set)

            if actual == objetivo:
                # Reconstruir camino
                camino = []
                while actual in came_from:
                    camino.append(actual)
                    actual = came_from[actual]
                camino.append(inicio)
                camino.reverse()
                return camino

            for vecino in self._vecinos(actual, mapa):
                tentative_g_score = g_score[actual] + 1
                if vecino not in g_score or tentative_g_score < g_score[vecino]:
                    came_from[vecino] = actual
                    g_score[vecino] = tentative_g_score
                    f_score[vecino] = tentative_g_score + self._heuristica(vecino, objetivo)
                    heapq.heappush(open_set, (f_score[vecino], vecino))

        return None  # No hay camino
    
    def _calcular_direccion(dx, dy):
        if dx == -1: return 0  # Norte
        elif dy == 1: return 1  # Este
        elif dx == 1: return 2  # Sur
        elif dy == -1: return 3  # Oeste


    def go_to(self, posicion_original, posicion_destino):
        """
        Mueve el robot a la posición destino usando A*.
        """
        mapa = self.estado_robot.mapa
        camino = self._a_star(mapa, posicion_original, posicion_destino)

        if not camino:
            print("No se encontró un camino.")
            return False

        orientacion_actual = self.estado_robot.orientacion
        x, y = posicion_original

        for siguiente in camino[1:]:  # Saltamos la posición inicial
            dx = siguiente[0] - x
            dy = siguiente[1] - y
            nueva_orientacion = self._calcular_direccion(dx, dy)

            # Girar si es necesario
            if nueva_orientacion != orientacion_actual:
                girar(orientacion_actual, nueva_orientacion)
                orientacion_actual = nueva_orientacion

            # Avanzar
            avanzar()

            # Actualizar estado interno
            x, y = siguiente
            self.estado_robot.nueva_celda(x, y)

        self.estado_robot.orientacion = orientacion_actual
        return True


    def orientate_to_base(self, posicion_base, aruco_detector, camera):
        """
        Orienta el robot hacia la base utilizando un marcador ArUco.
        :param posicion_base: Posición de la base (x, y).
        :param aruco_detector: Detector de marcadores ArUco.
        :param camera: Cámara para capturar imágenes.
        """
        orientacion_actual = self.estado_robot.orientacion

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

                    diferencia = center_x - frame_center_x
                    
                    if abs(diferencia) < 20:
                        print("Base centrada, orientación completa.")
                        break  # Ya está alineado
                   
                    # Aquí simulamos giro incremental. Puedes usar una orientación temporal.
                    # Si el marcador está a la derecha, gira hacia la derecha (suma 1 modulo 4)
                    if diferencia > 0:
                        nueva_orientacion = (orientacion_actual + 1) % 4
                    else:
                        nueva_orientacion = (orientacion_actual - 1) % 4

                    girar(orientacion_actual, nueva_orientacion)
                    orientacion_actual = nueva_orientacion
                    self.estado_robot.orientacion = orientacion_actual
            
            time.sleep(0.1)  # Pequeña pausa entre giros

    def explorar(self):
        # Aquí podrías llamar a detect_frontiers y usar go_to para moverte a la frontera más cercana
        frontiers = detect_frontiers(self.estado_robot.mapa)
        objetivo = get_closest_frontier(frontiers, self.estado_robot.celda_actual.get_posicion())
        if objetivo:
            self.go_to(self.estado_robot.celda_actual.get_posicion(), objetivo)
        else:
            print("No quedan fronteras para explorar")

    def volver_a_base(self, aruco_detector=None, camera=None):
        """
        Hace que el robot regrese a la base desde su posición actual.
        """
        mapa = self.estado_robot.mapa
        posicion_actual = self.estado_robot.posicion
        posicion_base = self.estado_robot.base
        orientacion = self.estado_robot.orientacion

        # Calcular el camino a la base
        camino = self._a_star(mapa, posicion_actual, posicion_base)

        if not camino:
            print("No se pudo calcular el camino a la base.")
            return False

        # Recorrer el camino (empezamos desde la segunda celda, ya que la primera es la actual)
        for siguiente_pos in camino[1:]:
            x_actual, y_actual = self.estado_robot.posicion
            x_siguiente, y_siguiente = siguiente_pos

            # Calcular nueva orientación deseada
            dx = x_siguiente - x_actual
            dy = y_siguiente - y_actual

            if dx == -1:
                nueva_orientacion = 0  # norte
            elif dx == 1:
                nueva_orientacion = 2  # sur
            elif dy == 1:
                nueva_orientacion = 1  # este
            elif dy == -1:
                nueva_orientacion = 3  # oeste
            else:
                print("Movimiento inválido.")
                continue

            # Girar si es necesario
            if orientacion != nueva_orientacion:
                girar(orientacion, nueva_orientacion)
                orientacion = nueva_orientacion

            # Avanzar una celda (se asume que la distancia es 1 unidad)
            avanzar(distancia=1)
            self.estado_robot.nueva_celda(x_siguiente, y_siguiente, orientacion)

        print("Llegada a la base.")

        # Orientarse hacia el marcador ArUco si se proporcionan detector y cámara
        if aruco_detector is not None and camera is not None:
            self.orientate_to_base(posicion_base, aruco_detector, camera)
