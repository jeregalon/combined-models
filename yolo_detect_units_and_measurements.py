import os
import glob
import cv2
from ultralytics import YOLO

# Carpetas de entrada y salida
carpeta_entrada = "Entradas"
carpeta_salida = "Salidas"
os.makedirs(carpeta_salida, exist_ok=True)

# Extensiones soportadas
ext_img = (".jpg", ".jpeg", ".png", ".bmp")
ext_vid = (".mp4", ".avi", ".mov", ".mkv", ".wmv")

# Cargar modelo
model = YOLO("units_and_measurements.pt")

# Buscar todos los archivos en la carpeta
archivos = glob.glob(os.path.join(carpeta_entrada, "*"))

for archivo in archivos:
    nombre_archivo = os.path.basename(archivo)
    nombre_sin_ext, ext = os.path.splitext(nombre_archivo)

    # Procesar imágenes
    if ext.lower() in ext_img:
        results = model(archivo)
        for result in results:
            annotated_img = result.plot()
            ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
            cv2.imwrite(ruta_salida, annotated_img)
            print(f"[IMG] Guardado: {ruta_salida}")

    # Procesar videos
    elif ext.lower() in ext_vid:
        cap = cv2.VideoCapture(archivo)
        if not cap.isOpened():
            print(f"No se pudo abrir el video: {archivo}")
            continue

        # Configurar video de salida
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ruta_video_salida = os.path.join(carpeta_salida, f"{nombre_sin_ext}_det.mp4")
        out = cv2.VideoWriter(ruta_video_salida, fourcc, fps, (width, height))

        print(f"[VID] Procesando video: {archivo}")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        cap.release()
        out.release()
        print(f"[VID] Guardado: {ruta_video_salida}")

print("Procesamiento completado.")
