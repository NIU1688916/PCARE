import cv2
import orbslam2
import numpy as np
from camara import RaspberryPiCamera  # Tu clase personalizada para la PiCam
import time

class ORBSLAM2Mapper:
    def __init__(self, vocab_path, settings_path, resolution=(640, 480), framerate=30):
        """
        Inicializa el sistema ORB-SLAM2 y la cámara monocular.
        """
        print("Iniciando ORB-SLAM2...")
        self.slam = orbslam2.System(
            vocab_path,
            settings_path,
            orbslam2.Sensor.MONOCULAR
        )
        self.slam.set_use_viewer(True)
        self.slam.initialize()

        # Inicializa la cámara
        self.camera = RaspberryPiCamera(0, resolution, framerate)
        self.camera.start_camera()

    def generar_mapeo_habitacion(self):
        """
        Captura un fotograma y lo procesa con ORB-SLAM2.
        """
        try:
            frame = self.camera.capture_frame()
            if frame is None:
                print("No se capturó ningún fotograma.")
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Timestamp necesario para ORB-SLAM2
            timestamp = time.time()
            self.slam.process_image_mono(gray, timestamp)

        except Exception as e:
            print(f"Error al procesar imagen: {e}")

    def obtener_posicion_2d_xy(self):
        """
        Devuelve la posición 2D del robot en el plano XY y orientación (theta).
        """
        pose = self.slam.get_frame_pose()
        if pose is None:
            print("⚠️ Pose aún no disponible.")
            return None

        T = pose
        x = T[0, 3]
        y = T[1, 3]

        dx = T[0, 0]
        dy = T[1, 0]
        theta = np.arctan2(dy, dx)

        return x, y, theta

    def cerrar(self):
        """
        Libera los recursos del SLAM y la cámara.
        """
        self.slam.shutdown()
        self.camera.stop_camera()
