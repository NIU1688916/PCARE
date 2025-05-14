import cv2

class RaspberryPiCamera:
    def __init__(self, camera_index=0, resolution=(640, 480), framerate=30):
        """
        Inicializa la cámara de la Raspberry Pi.
        :param camera_index: Índice de la cámara (por defecto 0).
        :param resolution: Resolución de la cámara (ancho, alto).
        :param framerate: Tasa de fotogramas por segundo.
        """
        self.camera_index = camera_index
        self.resolution = resolution
        self.framerate = framerate
        self.cap = None

    def start_camera(self):
        """
        Inicia la cámara y configura los parámetros.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.framerate)

        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara.")

    def capture_frame(self):
        """
        Captura un fotograma de la cámara.
        :return: El fotograma capturado.
        """
        if self.cap is None or not self.cap.isOpened():
            raise Exception("La cámara no está inicializada.")

        ret, frame = self.cap.read()
        if not ret:
            raise Exception("No se pudo capturar el fotograma.")
        return frame

    def stop_camera(self):
        """
        Libera los recursos de la cámara.
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __del__(self):
        """
        Asegura que los recursos se liberen al destruir la instancia.
        """
        self.stop_camera()