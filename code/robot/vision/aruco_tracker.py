import cv2
import numpy as np
import cv2.aruco as aruco

def detectar_aruco_y_orientacion(id_objetivo=0, cam_index=0):
    """
    Detecta un marcador ArUco y devuelve el ángulo de orientación.
    Compatible con la cámara de la Raspberry Pi.

    :param id_objetivo: ID del marcador ArUco que representa la base
    :param cam_index: Índice de la cámara (usualmente 0)
    :return: ángulo en grados o None si no se detecta
    """
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return None

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("No se pudo capturar imagen.")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parametros = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(diccionario, parametros)
    esquinas, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, id_detectado in enumerate(ids.flatten()):
            if id_detectado == id_objetivo:
                esquina = esquinas[i][0]
                # Tomamos dos puntos para estimar orientación
                punto1, punto2 = esquina[0], esquina[1]
                dx = punto2[0] - punto1[0]
                dy = punto2[1] - punto1[1]
                angulo = np.degrees(np.arctan2(dy, dx))
                return angulo

    return None
