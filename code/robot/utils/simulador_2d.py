import time
import os
import random
import matplotlib.pyplot as plt
import numpy as np

# Parámetros del mapa
tamano_x = 20
tamano_y = 30

# Códigos para imprimir el mapa
VACIO = '.'
OBSTACULO = '#'
ROBOT = 'R'
DESTINO = 'D'
RECORRIDO = '*'

# Orientaciones: 0=Norte, 1=Este, 2=Sur, 3=Oeste
direcciones = [(-1,0), (0,1), (1,0), (0,-1)]
simbolos_orientacion = ['^', '>', 'v', '<']

class Celda:
    def __init__(self, es_obstaculo=False):
        self.es_obstaculo = es_obstaculo
        self.es_visitado = False

class SimuladorRobot:
    def __init__(self, mapa, inicio, destino, usar_sensores=False):
        self.mapa = mapa  # Mapa real (completo)
        self.pos = inicio
        self.destino = destino
        self.orientacion = 0  # Norte
        self.recorrido = set()
        self.usar_sensores = usar_sensores
        if usar_sensores:
            # Mapa conocido por el robot (al principio solo sabe su celda)
            self.mapa_conocido = [[None for _ in range(tamano_y)] for _ in range(tamano_x)]
            x, y = self.pos
            self.mapa_conocido[x][y] = Celda(es_obstaculo=False)
            self.descubrir_vecinos(x, y)
        else:
            self.mapa_conocido = self.mapa  # Ve todo

    def descubrir_vecinos(self, x, y):
        # Simula sensores: descubre las celdas adyacentes
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            if 0 <= nx < tamano_x and 0 <= ny < tamano_y:
                if self.mapa_conocido[nx][ny] is None:
                    real = self.mapa[nx][ny]
                    self.mapa_conocido[nx][ny] = Celda(es_obstaculo=real.es_obstaculo)

    def mostrar_mapa(self):
        # Visualización con matplotlib
        mapa_a_mostrar = self.mapa_conocido if self.usar_sensores else self.mapa
        grid = np.zeros((len(mapa_a_mostrar), len(mapa_a_mostrar[0]), 3))  # RGB
        for i in range(len(mapa_a_mostrar)):
            for j in range(len(mapa_a_mostrar[0])):
                if (i, j) == self.pos:
                    grid[i, j] = [0, 1, 0]  # Verde para el robot
                elif self.usar_sensores and mapa_a_mostrar[i][j] is None:
                    grid[i, j] = [0.8, 0.8, 0.8]  # Gris claro para desconocido
                elif mapa_a_mostrar[i][j] and mapa_a_mostrar[i][j].es_obstaculo:
                    grid[i, j] = [1, 0, 0]  # Rojo para obstáculo
                elif hasattr(self, 'historial_lecturas') and (i, j) in self.historial_lecturas:
                    # Azul si se ha hecho lectura aquí
                    grid[i, j] = [0.2, 0.4, 1]
                elif (i, j) in self.recorrido:
                    grid[i, j] = [0.5, 0.5, 1]  # Azul claro para recorrido
                else:
                    grid[i, j] = [1, 1, 1]  # Blanco para libre
        plt.clf()
        plt.imshow(grid, interpolation='none')
        plt.title(f'Posición robot: {self.pos}')
        plt.axis('off')
        plt.pause(0.01)

    def avanzar(self):
        dx, dy = direcciones[self.orientacion]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        if 0 <= nx < tamano_x and 0 <= ny < tamano_y:
            celda = self.mapa[nx][ny] if not self.usar_sensores else self.mapa_conocido[nx][ny]
            if celda and not celda.es_obstaculo:
                self.pos = (nx, ny)
                self.recorrido.add(self.pos)
                if self.usar_sensores:
                    self.descubrir_vecinos(nx, ny)
                return True
        return False

    def girar(self, nueva_orientacion):
        self.orientacion = nueva_orientacion

    def _heuristica(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _vecinos(self, nodo):
        vecinos = []
        x, y = nodo
        for idx, (dx, dy) in enumerate(direcciones):
            nx, ny = x + dx, y + dy
            if 0 <= nx < tamano_x and 0 <= ny < tamano_y:
                celda = self.mapa[nx][ny] if not self.usar_sensores else self.mapa_conocido[nx][ny]
                if celda and not celda.es_obstaculo:
                    vecinos.append((nx, ny))
        return vecinos

    def calcular_direccion(self, actual, siguiente):
        dx = siguiente[0] - actual[0]
        dy = siguiente[1] - actual[1]
        for idx, (ddx, ddy) in enumerate(direcciones):
            if dx == ddx and dy == ddy:
                return idx
        return self.orientacion

    def a_star(self, inicio, objetivo):
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, inicio))
        came_from = {}
        g_score = {inicio: 0}
        f_score = {inicio: self._heuristica(inicio, objetivo)}
        while open_set:
            _, actual = heapq.heappop(open_set)
            if actual == objetivo:
                camino = []
                while actual in came_from:
                    camino.append(actual)
                    actual = came_from[actual]
                camino.append(inicio)
                camino.reverse()
                return camino
            for vecino in self._vecinos(actual):
                tentative_g_score = g_score[actual] + 1
                if vecino not in g_score or tentative_g_score < g_score[vecino]:
                    came_from[vecino] = actual
                    g_score[vecino] = tentative_g_score
                    f_score[vecino] = tentative_g_score + self._heuristica(vecino, objetivo)
                    heapq.heappush(open_set, (f_score[vecino], vecino))
        return None

    def calcular_direccion(self, actual, siguiente):
        dx = siguiente[0] - actual[0]
        dy = siguiente[1] - actual[1]
        for idx, (ddx, ddy) in enumerate(direcciones):
            if dx == ddx and dy == ddy:
                return idx
        return self.orientacion

    def go_to(self):
        camino = self.a_star(self.pos, self.destino)
        if not camino:
            print("No se encontró un camino.")
            return False
        for siguiente in camino[1:]:
            nueva_orientacion = self.calcular_direccion(self.pos, siguiente)
            if nueva_orientacion != self.orientacion:
                self.girar(nueva_orientacion)
            exito = self.avanzar()
            self.mostrar_mapa()
            time.sleep(0.3)
            if not exito:
                print("Obstáculo inesperado. Abortando.")
                return False
        print("¡Llegamos al destino!")
        return True

    def explorar_con_sensores(self):
        """
        Exploración tipo frontier: el robot explora hasta descubrir el destino.
        """
        from collections import deque
        while True:
            # Si el destino ya es conocido, intenta ir a él
            dx, dy = self.destino
            if self.mapa_conocido[dx][dy] is not None:
                print("Destino descubierto, intentando llegar...")
                exito = self.go_to()
                if exito:
                    print("¡Llegamos al destino!")
                else:
                    print("No se pudo llegar al destino.")
                break
            # Buscar la frontera más cercana (celda libre desconocida adyacente a conocida)
            frontera = self.buscar_frontera()
            if frontera is None:
                print("No quedan fronteras para explorar y no se encontró el destino.")
                break
            print(f"Explorando hacia frontera más cercana: {frontera}")
            self.go_to_objetivo(frontera)
            os.system('clear')

    def buscar_frontera(self):
        """
        Busca la celda frontera más cercana (adyacente a zona desconocida y accesible).
        """
        from collections import deque
        visitado = set()
        queue = deque()
        queue.append(self.pos)
        while queue:
            actual = queue.popleft()
            if actual in visitado:
                continue
            visitado.add(actual)
            x, y = actual
            if self.mapa_conocido[x][y] and not self.mapa_conocido[x][y].es_obstaculo:
                # ¿Tiene algún vecino desconocido?
                for dx, dy in direcciones:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < tamano_x and 0 <= ny < tamano_y:
                        if self.mapa_conocido[nx][ny] is None:
                            return (x, y)
                # Si no, seguir explorando
                for vecino in self._vecinos((x, y)):
                    if vecino not in visitado:
                        queue.append(vecino)
        return None

    def go_to_objetivo(self, objetivo):
        """
        Igual que go_to pero permite objetivo parcial (frontera).
        """
        camino = self.a_star(self.pos, objetivo)
        if not camino:
            print("No se encontró un camino a la frontera.")
            return False
        for siguiente in camino[1:]:
            nueva_orientacion = self.calcular_direccion(self.pos, siguiente)
            if nueva_orientacion != self.orientacion:
                self.girar(nueva_orientacion)
            exito = self.avanzar()
            self.mostrar_mapa()
            time.sleep(0.2)
            if not exito:
                print("Obstáculo inesperado. Abortando.")
                return False
        return True

    def leer_sensores(self):
        # Simulación de sensores: valores aleatorios
        humedad = random.randint(0, 100)  # 0-100%
        luz = random.randint(0, 1000)     # 0-1000 lux
        return humedad, luz

    def guardar_lectura(self, x, y, humedad, luz):
        if not hasattr(self, 'historial_lecturas'):
            self.historial_lecturas = {}
        self.historial_lecturas[(x, y)] = {'humedad': humedad, 'luz': luz}

    def exploracion_infinita(self, cada_n=10, umbral_humedad=30):
        from collections import deque
        pasos = 0
        while True:
            frontera = self.buscar_frontera()
            if frontera is None:
                print("No quedan fronteras para explorar. Exploración terminada.")
                break
            print(f"Explorando hacia frontera más cercana: {frontera}")
            self.go_to_objetivo(frontera)
            self.mostrar_mapa()
            pasos += 1
            if pasos % cada_n == 0:
                x, y = self.pos
                humedad, luz = self.leer_sensores()
                self.guardar_lectura(x, y, humedad, luz)
                print(f"Lectura en celda {self.pos}: humedad={humedad}, luz={luz}")
                if humedad < umbral_humedad:
                    print(f"¡Humedad baja ({humedad}%)! Simulando riego...")
                    time.sleep(5)  # Simula el tiempo de riego
                    print("Riego completado. Continuando exploración...")
            time.sleep(0.1)
            if pasos % 50 == 0:
                print(f"Llevamos {pasos} pasos de exploración.")
        
            

def crear_mapa():
    # Mapa grande vacío con obstáculos aleatorios
    #tamano_x = 20
    #tamano_y = 30
    mapa = [[Celda() for _ in range(tamano_y)] for _ in range(tamano_x)]
    random.seed(42)
    for _ in range(120):
        x, y = random.randint(0, tamano_x-1), random.randint(0, tamano_y-1)
        if (x, y) != (0, 0):
            mapa[x][y].es_obstaculo = True
    return mapa, tamano_x, tamano_y

if __name__ == "__main__":
    plt.ion()  # Modo interactivo
    mapa, tamano_x, tamano_y = crear_mapa()
    inicio = (0, 0)
    usar_sensores = True  # Solo modo exploración
    robot = SimuladorRobot(mapa, inicio, destino=None, usar_sensores=usar_sensores)
    robot.mostrar_mapa()
    input("Presiona Enter para comenzar la exploración infinita...")
    robot.exploracion_infinita(cada_n=10)  # Cambia cada_n para ajustar la frecuencia de lectura
    input("Presiona Enter para salir...")
