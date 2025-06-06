import cv2
from camara import RaspberryPiCamera  # Tu clase personalizada para la PiCam
from pyslam.slam import SLAM
import numpy as np

class ORBSLAM2Mapper:
    def __init__(self, camera_index=0, resolution=(640, 480), framerate=30):
        """
        Inicializa el sistema ORB-SLAM2 (pyslam) y la cámara monocular.
        """
        # Parámetros de la cámara (debes ajustarlos a tu cámara real)
        self.camera_matrix = [530.0, 530.0, resolution[0] / 2, resolution[1] / 2]  # fx, fy, cx, cy
        self.distortion = [0, 0, 0, 0, 0]  # Sin distorsión por ahora

        # Inicializa SLAM
        self.slam = SLAM(camera_matrix=self.camera_matrix,
                         distortion=self.distortion,
                         use_viewer=True)

        # Inicializa la cámara
        self.camera = RaspberryPiCamera(camera_index, resolution, framerate)
        self.camera.start_camera()

    def generar_mapeo_habitacion(self):
        """
        Captura un fotograma y lo procesa con pyslam.
        """
        try:
            frame = self.camera.capture_frame()
            if frame is None:
                print("No se capturó ningún fotograma.")
                return

            # Convertimos a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Procesar imagen con pyslam
            self.slam.track(gray)

            # Devolver mapa si está disponible
            if self.slam.map is not None:
                return self.slam.map
            else:
                print("Mapa no disponible aún.")
        except Exception as e:
            print(f"Error al procesar imagen: {e}")

    def obtener_posicion_2d_xy(self):
        """
        Devuelve la posición 2D del robot en el plano XY y orientación (theta).
        """
        frame = self.camera.capture_frame()
        if frame is None:
            print("No se capturó ningún fotograma.")
            return

        # Convertimos a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Procesar imagen con pyslam
        self.slam.track(gray)

        if self.slam.Twc is not None:
            T = self.slam.Twc
            x = T[0, 3]  # posición en X
            y = T[1, 3]  # posición en Y

            # Extraer orientación: ángulo theta respecto al eje Z (plano XY)
            # Tomamos el eje X o Y del sistema de cámara (R = T[:3, :3])
            # Por convención, tomamos el eje X de la cámara proyectado en XY:
            dx = T[0, 0]
            dy = T[1, 0]
            theta = np.arctan2(dy, dx)  # orientación en radianes

            return x, y, theta
        else:
            print("⚠️ Pose aún no disponible.")
            return None

    def exportar_mapa_png(self, modo='XZ', tamano=(800, 800), zoom=50):
            """
            Exporta una imagen 2D del mapa generado por pyslam en formato PNG.
            
            :param archivo_salida: Nombre del archivo PNG de salida.
            :param modo: Plano de proyección: 'XY', 'XZ' o 'YZ'.
            :param tamano: Tamaño de la imagen resultante (ancho, alto).
            :param zoom: Factor de escalado para visualizar mejor.
            """
            if self.slam.map is None:
                print("⚠️  No hay mapa disponible para exportar.")
                return

            puntos = [mp.pt for mp in self.slam.map.map_points.values()]
            puntos = np.array(puntos)

            if puntos.shape[0] == 0:
                print("⚠️  No hay puntos suficientes en el mapa.")
                return

            # Elegir los ejes a proyectar
            if modo == 'XY':
                coords = puntos[:, [0, 1]]
            elif modo == 'XZ':
                coords = puntos[:, [0, 2]]
            elif modo == 'YZ':
                coords = puntos[:, [1, 2]]
            else:
                print("⚠️  Modo inválido. Usa 'XY', 'XZ' o 'YZ'.")
                return

            # Escalado y normalización
            coords *= zoom
            coords -= coords.min(axis=0)
            coords = coords.astype(np.int32)

            # Crear imagen blanca
            img = np.ones((tamano[1], tamano[0]), dtype=np.uint8) * 255

            # Dibujar puntos
            for x, y in coords:
                if 0 <= x < tamano[0] and 0 <= y < tamano[1]:
                    img[y, x] = 0  # negro = punto
            return img


    def cerrar(self):
        """
        Libera los recursos del SLAM y la cámara.
        """
        self.camera.stop_camera()
        self.slam.shutdown()
