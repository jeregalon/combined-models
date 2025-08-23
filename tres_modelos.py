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
model_obb = YOLO("digital_hand_scales_obb.pt")
model_segment = YOLO("displays_segment.pt")

# Buscar todos los archivos en la carpeta
input_files = glob.glob(os.path.join(input_folder, "*"))
archivos_obb = glob.glob(os.path.join(output_folder, "*"))

for file in input_files:
    file_name = os.path.basename(file)
    file_name_without_ext, ext = os.path.splitext(file_name)

    if ext.lower() in ext_img:
        img_array = cv2.imread(file)     # convertir la foto en un array de NumPy
        detected_scales = model_obb(img_array)     # detectar las pesas en la foto
        trimmed_scales_list = []
        trimmed_displays_list = []

        # for i, result in enumerate(detected_scales):            
        #     # Dibujar las cajas en la imagen
        #     annotated_img = result.plot()

        #     # Guardar la imagen anotada
        #     resized = cv2.resize(annotated_img, (320, 320))
        #     cv2.imshow("detected_scale", resized)
        #     cv2.waitKey(0)

        scales = detected_scales[0].obb 
        xywhr_list = scales.xywhr.squeeze().tolist()    # coordenadas de las cajas delimitadoras (OBB)
        
        if is_plane(xywhr_list):
            if scales.conf > 0.6:
                trimmed_scales_list.append(trim_box(img_array, xywhr_list))
        else:
            for i, box in enumerate(xywhr_list):
                if scales.conf[i] > 0.6:
                    trimmed_scales_list.append(trim_box(img_array, box))

        # for i in range(len(trimmed_scales_list)):

        #     ruta_guardado = os.path.join(output_folder, f"{file_name_without_ext}_scale_{i}.jpg")
        #     cv2.imwrite(ruta_guardado, trimmed_scales_list[i])

        for trimmed_scale in trimmed_scales_list:
            # detectar displays
            detected_displays = model_segment(trimmed_scale)
            masks = detected_displays[0].masks
            if masks != None:
                for i, display_mask in enumerate(masks.xy):
                    if detected_displays[0].boxes.conf[i] > 0.6:
                        trimmed_displays_list.append(trim_mask(trimmed_scale, display_mask))

        # for i in range(len(trimmed_displays_list)):
            
        #     ruta_guardado = os.path.join(output_folder, f"{file_name_without_ext}_display_{i}.jpg")
        #     cv2.imwrite(ruta_guardado, trimmed_displays_list[i])



            

#         for result in results:
#             xywhr_list = result.obb.xywhr.squeeze().tolist()    # coordenadas de la caja delimitadora (OBB)
#             current_frame = cv2.imread(archivo) # convierto la ruta en un array de NumPy

#             if (len(xywhr_list) == 5):
#                 recortar_caja(current_frame, xywhr_list)
#             else:
#                 print("El archivo {archivo} no se pudo procesar")
    
# for archivo in archivos_obb:
#     nombre_archivo = os.path.basename(archivo)
#     nombre_sin_ext, ext = os.path.splitext(nombre_archivo)

#     # Detectar display
#     if ext.lower() in ext_img:
#         results = model_segment(archivo)
#         for result in results:
#             current_frame = cv2.imread(archivo) # convierto la ruta en un array de NumPy
#             if result.masks != None:
#                 recortar_mascara(current_frame, result.masks.xy)



    # # Procesar videos
    # elif ext.lower() in ext_vid:
    #     cap = cv2.VideoCapture(archivo)
    #     if not cap.isOpened():
    #         print(f"No se pudo abrir el video: {archivo}")
    #         continue

    #     # Configurar video de salida
    #     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #     fps = cap.get(cv2.CAP_PROP_FPS)
    #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     ruta_video_salida = os.path.join(output_folder, f"{nombre_sin_ext}_det.mp4")
    #     out = cv2.VideoWriter(ruta_video_salida, fourcc, fps, (width, height))

    #     print(f"[VID] Procesando video: {archivo}")

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break

    #         results = model(frame, verbose=False)
    #         annotated_frame = results[0].plot()
    #         out.write(annotated_frame)

    #     cap.release()
    #     out.release()
    #     print(f"[VID] Guardado: {ruta_video_salida}")

# print("Procesamiento completado.")
