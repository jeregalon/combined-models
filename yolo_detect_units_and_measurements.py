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
model = YOLO("units_and_measurements.pt")
model_ch = YOLO("best_yolo11n.pt")

# Buscar todos los archivos en la carpeta
archivos = glob.glob(os.path.join(carpeta_entrada, "*"))

for archivo in archivos:
    nombre_archivo = os.path.basename(archivo)
    nombre_sin_ext, ext = os.path.splitext(nombre_archivo)

    # Procesar imágenes
    if ext.lower() in ext_img:
        img_array = cv2.imread(archivo)
        results = model(archivo)
        for result in results:
            rotated_image = rotate(img_array, result.obb)
            detected_characters = model_ch(rotated_image)
            hay_punto = (detected_characters[0].boxes.cls == 0).any().item()
            if not hay_punto:
                rotated_image = rotate_180(rotated_image)
                detected_characters = model_ch(rotated_image)
            characters_coords = []
            xywh_list = detected_characters[0].boxes.xywh.squeeze().tolist()
            for i, box in enumerate(xywh_list):
                character_class = int(detected_characters[0].boxes.cls[i].item())
                character_conf = detected_characters[0].boxes.conf[i].item()
                characters_coords.append([box[0], character_class, character_conf])

            ceros = [v for v in characters_coords if v[1] == 0]
            otros = [v for v in characters_coords if v[1] != 0]

            if ceros:
                mejor_cero = max(ceros, key=lambda v: v[2])  # el de mayor confianza
                coords_filtrados = otros + [mejor_cero]
            else:
                coords_filtrados = characters_coords

            # 2. Ordenar por coordenada x
            coords_ordenados = sorted(coords_filtrados, key=lambda v: v[0])

            # 3. Mapeo de clases a caracteres
            mapa = {
                0: ".",
                1: "0",
                2: "1",
                3: "2",
                4: "3",
                5: "4",
                6: "5",
                7: "6",
                8: "7",
                9: "8",
                10: "9"
            }

            # 4. Crear string lectura
            lectura = "".join(mapa[v[1]] for v in coords_ordenados)
            print("Lectura:", lectura)

            annotated_img = detected_characters[0].plot()
            ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
            cv2.imwrite(ruta_salida, annotated_img)

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
