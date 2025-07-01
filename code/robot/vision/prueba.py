import cv2
import numpy as np
from camara import RaspberryPiCamera  # Tu clase personalizada
from pyslam.slam import SLAM
import time

def generar_imagen_mapa(slam, modo='XZ', tamano=(800, 800), zoom=50):
    """
    Devuelve una imagen 2D del mapa SLAM con los puntos proyectados.
    """
    if slam.map is None:
        return None

    puntos = [mp.pt for mp in slam.map.map_points.values()]
    if len(puntos) == 0:
        return None

    puntos = np.array(puntos)

    # Elegir los ejes para proyección
    if modo == 'XY':
        coords = puntos[:, [0, 1]]
    elif modo == 'XZ':
        coords = puntos[:, [0, 2]]
    elif modo == 'YZ':
        coords = puntos[:, [1, 2]]
    else:
        print("Modo de proyección inválido.")
        return None

    # Escalado y normalización
    coords *= zoom
    coords -= coords.min(axis=0)
    coords = coords.astype(np.int32)

    # Crear imagen blanca
    img = np.ones((tamano[1], tamano[0]), dtype=np.uint8) * 255

    # Dibujar puntos negros
    for x, y in coords:
        if 0 <= x < tamano[0] and 0 <= y < tamano[1]:
            img[y, x] = 0

    return img

def main():
    resolution = (640, 480)
    camera_matrix = [530.0, 530.0, resolution[0]/2, resolution[1]/2]
    distortion = [0, 0, 0, 0, 0]

    cam = RaspberryPiCamera(camera_index=0, resolution=resolution, framerate=30)
    cam.start_camera()

    slam = SLAM(camera_matrix=camera_matrix,
                distortion=distortion,
                use_viewer=False)  # Desactivamos viewer interno, usamos OpenCV

    print("🔁 SLAM monocular en ejecución...")

    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            slam.track(gray)

            # Mostrar posición
            if slam.Twc is not None:
                T = slam.Twc
                x, y = T[0, 3], T[1, 3]
                dx, dy = T[0, 0], T[1, 0]
                theta = np.arctan2(dy, dx)
                print(f"📍 x={x:.2f}, y={y:.2f}, θ={np.degrees(theta):.1f}°")
            else:
                print("⚠️ Pose aún no disponible.")

            # Mostrar frame
            cv2.imshow("Frame monocular", frame)

            # Mostrar mapa SLAM
            mapa_img = generar_imagen_mapa(slam)
            if mapa_img is not None:
                cv2.imshow("Mapa SLAM (XZ)", mapa_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por teclado.")
    finally:
        cam.stop_camera()
        slam.shutdown()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
