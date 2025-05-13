import cv2
import cv2.aruco as aruco

def detectar_aruco(frame, camera_matrix, dist_coeffs):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    if ids is not None:
        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
        return ids, corners, rvec, tvec
    return None, None, None, None
