import cv2
import orbslam2
from camara import RaspberryPiCamera 

class ORBSLAM2Mapper:
    def __init__(self, camera_params_path, camera_index=0, resolution=(640, 480), framerate=30):
        """
        Inicializa el sistema ORB-SLAM2 y la cámara.
        :param camera_params_path: Ruta al archivo de parámetros de la cámara.
        :param camera_index: Índice de la cámara (por defecto 0).
        :param resolution: Resolución de la cámara (ancho, alto).
        :param framerate: Tasa de fotogramas por segundo.
        """
        self.slam = orbslam2.System(camera_params_path, orbslam2.Sensor.MONOCULAR)
        self.slam.initialize()

        # Inicializar la cámara
        self.camera = RaspberryPiCamera(camera_index, resolution, framerate)
        self.camera.start_camera()

    def generar_mapeo_habitacion(self):
        """
        Captura un fotograma de la cámara y lo procesa con ORB-SLAM2 para generar el mapa.
        """
        #TODO:Nose si funciona, hay que probarlo y modificarlo
        try:
            # Capturar un fotograma de la cámara
            frame = self.camera.capture_frame()

            # Procesar la imagen con ORB-SLAM2
            pose = self.slam.process_image(frame)

            # Actualizar el mapa del robot si se obtuvo una pose válida
            if pose is not None:
                return self.slam.get_map_points()
            else:
                print("No se pudo procesar la imagen para generar el mapa.")
        except Exception as e:
            print(f"Error al generar el mapeo de la habitación: {e}")

    def cerrar(self):
        """
        Libera los recursos de ORB-SLAM2 y la cámara.
        """
        self.slam.shutdown()
        self.camera.stop_camera()