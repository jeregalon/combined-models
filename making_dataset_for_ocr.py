import os
import glob
import cv2
from ultralytics import YOLO
import numpy as np
from funciones import *

# Carpetas de entrada y salida
input_folder = "Entradas"
output_folder = "Salidas"
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Extensiones soportadas
ext_img = (".jpg", ".jpeg", ".png", ".bmp")
ext_vid = (".mp4", ".avi", ".mov", ".mkv", ".wmv")

# Cargar modelos
model_1 = YOLO("displays_segment.pt")
model_2 = YOLO("units_and_measurements.pt")

# Buscar todos los archivos en la carpeta
input_files = glob.glob(os.path.join(input_folder, "*"))

for file in input_files:
    file_name = os.path.basename(file)
    file_name_without_ext, ext = os.path.splitext(file_name)

    if ext.lower() in ext_img:
        img_array = cv2.imread(file)     # convertir la foto en un array de NumPy
        detected_displays = model_1(img_array)     # detectar las pantallas en la foto
        trimmed_displays_list = []

        # for i, result in enumerate(detected_displays):            
        #     # Dibujar las cajas en la imagen
        #     annotated_img = result.plot()

        #     # Guardar la imagen anotada
        #     cv2.imshow("detected_display", annotated_img)
        #     cv2.waitKey(0)

        masks = detected_displays[0].masks
        if masks != None:
            for i, display_mask in enumerate(masks.xy):
                if detected_displays[0].boxes.conf[i] > 0.8:
                    trimmed_displays_list.append(trim_mask(img_array, display_mask))

        for i in range(len(trimmed_displays_list)):
            
            ruta_guardado = os.path.join(output_folder, f"{file_name_without_ext}_display_{i}.jpg")
            cv2.imwrite(ruta_guardado, trimmed_displays_list[i])

        for trimmed_display in trimmed_displays_list:
            # detectar la medida y la unidad en la pantalla
            detected_objects = model_2(trimmed_display)
            objects = detected_objects[0].obb 
            xywhr_list = objects.xywhr.squeeze().tolist()    # coordenadas de las cajas delimitadoras (OBB)

            if is_plane(xywhr_list):
                if objects.conf > 0.6:
                    ruta_guardado = os.path.join(output_folder, f"{file_name_without_ext}_scale_{i}.jpg")
                    cv2.imwrite(ruta_guardado, trim_box(img_array, xywhr_list))
            else:
                for i, box in enumerate(xywhr_list):
                    if objects.conf[i] > 0.6:
                        ruta_guardado = os.path.join(output_folder, f"{file_name_without_ext}_scale_{i}.jpg")
                        cv2.imwrite(ruta_guardado, trim_box(img_array, box))