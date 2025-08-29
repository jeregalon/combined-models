import os
import glob
import cv2
from ultralytics import YOLO
from funciones import *

# Carpetas de entrada y salida
carpeta_entrada = "Entradas"
carpeta_salida = "Salidas"
os.makedirs(carpeta_salida, exist_ok=True)

# Extensiones soportadas
ext_img = (".jpg", ".jpeg", ".png", ".bmp")
ext_vid = (".mp4", ".avi", ".mov", ".mkv", ".wmv")

# Cargar modelo
model = YOLO("digital_characters_obb_model.pt")
model_ch = YOLO("separated_characters_model.pt")

# Buscar todos los archivos en la carpeta
archivos = glob.glob(os.path.join(carpeta_entrada, "*"))

for archivo in archivos:
    nombre_archivo = os.path.basename(archivo)
    nombre_sin_ext, ext = os.path.splitext(nombre_archivo)

    # Procesar imágenes
    if ext.lower() in ext_img:
        img_array = cv2.imread(archivo)
        processed_image, reading = process_frame(model, model_ch, img_array)
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_archivo} {reading}.jpg")
        cv2.imwrite(ruta_salida, processed_image) 
    
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

            processed_image, reading = process_frame(model, model_ch, frame)
            out.write(processed_image)

        cap.release()
        out.release()
        print(f"[VID] Guardado: {ruta_video_salida}")

print("Procesamiento completado.")
