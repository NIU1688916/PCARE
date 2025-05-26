from motores import avanzar, retroceder,girar
import math
from frontier import detect_frontiers, get_closest_frontier
import heapq  # Para la cola de prioridad en A*
import time
from vision.aruco_tracker import detectar_aruco_y_orientacion

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
                if mapa[nx][ny].es_visitado == False:  # Solo celdas libres
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
        self.estado_robot.posicion = (x, y)
        return True


    def convertir_angulo_a_orientacion(angulo):
        if angulo < 45 or angulo >= 315:
            return 0  # Norte
        elif angulo < 135:
            return 1  # Este
        elif angulo < 225:
            return 2  # Sur
        else:
            return 3  # Oeste

    def orientate_to_base(self, orientacion_actual=0, id_aruco=0):
        """
        Orienta el robot hacia la base utilizando un marcador ArUco.
        """
        print("Buscando el marcador de la base...")
        angulo = detectar_aruco_y_orientacion(id_objetivo=id_aruco)
        
        if angulo is None:
            print("No se detectó el marcador de la base.")
            return
        
        print(f"Ángulo detectado: {angulo:.2f}°")
        
        nueva_orientacion = self.convertir_angulo_a_orientacion(angulo)
        girar(self.estado_robot.orientacion, nueva_orientacion)
             
        print("Robot orientado hacia el marcador de la base.")

    def explorar(self):
        # Aquí podrías llamar a detect_frontiers y usar go_to para moverte a la frontera más cercana
        frontiers = detect_frontiers(self.estado_robot.mapa)
        objetivo = get_closest_frontier(frontiers, self.estado_robot.celda_actual.get_posicion())
        if objetivo:
            self.go_to(self.estado_robot.celda_actual.get_posicion(), objetivo)
        else:
            print("No quedan fronteras para explorar")

    def volver_a_base(self):
        """
        Hace que el robot regrese a la base desde su posición actual.
        """
        base = self.estado_robot.base # (x,y)
        posicion_actual = self.estado_robot.posicion # (x,y)

        if posicion_actual == base:
            print("Ya estamos en la base.")
            return
        
        print(f"Volviendo a la base desde {posicion_actual} hacia {base}")

        self.go_to(posicion_actual, base)
        