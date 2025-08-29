import os
import numpy as np
import cv2

import cv2
import numpy as np

def rotate(image, coords, exit_folder="Salidas", file_name ="-1", output_name="-1"):
    xywhr_list = coords.xywhr.squeeze().tolist()
    # xywhr_class_list = []
    if is_plane(xywhr_list):
        # xywhr_list.append(int(coords.cls[0].item()))
        # xywhr_class_list.append(xywhr_list)
        x, y, w, h, r = xywhr_list
    else:
        # for i, box in enumerate(xywhr_list):
        #     box.append(int(coords.cls[i].item()))
        #     xywhr_class_list.append(box)
        idx = (coords.cls == 3).nonzero(as_tuple=True)[0]
        pos = idx.item()
        x, y, w, h, r = xywhr_list[pos]

    try:
        r = float(np.degrees(r))    # convertir r (rotación) a grados
    except:
        print("No se pudo extraer el ángulo de rotación de este elemento")
        return
    
    if w < h:
        w, h = h, w
        r += 90

    (h_img, w_img) = image.shape[:2]
    cx, cy = w_img // 2, h_img // 2   # centro de la imagen

    # Matriz de rotación (respecto al centro de la imagen)
    M = cv2.getRotationMatrix2D((cx, cy), r, 1.0)

    # Calcular nuevas dimensiones de la imagen
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h_img * sin) + (w_img * cos))
    new_h = int((h_img * cos) + (w_img * sin))

    # Ajustar la traslación de la matriz para centrar en el nuevo canvas
    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    # Aplicar rotación
    rotated_image = cv2.warpAffine(image, M, (new_w, new_h))

    if file_name != "-1":
        if output_name != "-1":
            image_name = f"{output_name}.jpg"
        else:
            image_name = f"{file_name} rotated.jpg"
        ruta_salida = os.path.join(exit_folder, image_name)
        cv2.imwrite(ruta_salida, rotated_image)
    
    return rotated_image, r, w_img, h_img

def rotate_angle(image, angle, exit_folder="Salidas", file_name ="-1", attempt = -1, output_name="-1"):
    alto, ancho = image.shape[:2]
    cx, cy = ancho // 2, alto // 2  # centro de la imagen

    # Matriz de rotación respecto al centro
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

    # Calcular nuevas dimensiones de la imagen rotada
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((alto * sin) + (ancho * cos))
    new_h = int((alto * cos) + (ancho * sin))

    # Ajustar traslación en la matriz para que no se pierda nada
    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    # Aplicar la rotación con el nuevo tamaño
    rotated_image = cv2.warpAffine(image, M, (new_w, new_h))

    if file_name != "-1":
        if output_name != "-1":
            image_name = f"{output_name}.jpg"
        else:
            attempt_str = f" {attempt} attempt" if attempt != -1 else ""
            image_name = f"{file_name} rotated{attempt_str}.jpg"
        ruta_salida = os.path.join(exit_folder, image_name)
        cv2.imwrite(ruta_salida, rotated_image)
    
    return rotated_image

def trim_box(image, coords):
    x, y, w, h, r = coords

    try:
        r = float(np.degrees(r))    # convertir r (rotación) a grados
    except:
        print("No se pudo extraer el ángulo de rotación de este elemento")
        return

    # --- EXPANDIR LIENZO ---
    h_img, w_img = image.shape[:2]
    expanded = np.zeros((h_img * 2, w_img * 2, 3), dtype=image.dtype)  # lienzo negro
    
    # posición de la imagen original en el centro del lienzo
    y_offset = h_img // 2
    x_offset = w_img // 2
    expanded[y_offset:y_offset+h_img, x_offset:x_offset+w_img] = image

    # actualizar coordenadas del centro (x, y) al nuevo sistema
    x = x + x_offset
    y = y + y_offset

    # --- CREAR MATRIZ DE ROTACIÓN ---
    M = cv2.getRotationMatrix2D((x, y), r, 1.0)  
    rotated_image = cv2.warpAffine(expanded, M, (expanded.shape[1], expanded.shape[0]))

    # --- RECORTE ---
    x_min = max(0, int(x - w/2))
    x_max = min(rotated_image.shape[1], int(x + w/2))
    y_min = max(0, int(y - h/2))
    y_max = min(rotated_image.shape[0], int(y + h/2))
    
    trim = rotated_image[y_min:y_max, x_min:x_max]
    return trim


def trim_mask(img, points):
    # Asegurar que los puntos son enteros
    pts = np.array(points, dtype=np.int32)
    pts = pts.reshape((-1, 1, 2))  # Formato que requiere OpenCV

    # Crear máscara en negro
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    # Dibujar el polígono en blanco
    cv2.fillPoly(mask, [pts], 255)

    # Aplicar la máscara a la imagen
    trim = cv2.bitwise_and(img, img, mask=mask)

    # Opcional: recortar al bounding box del polígono (para que no quede mucho negro alrededor)
    x, y, w, h = cv2.boundingRect(pts)
    trim = trim[y:y+h, x:x+w]
    return trim

    # Guardar imagen en la carpeta de salida
    # os.makedirs(carpeta_salida_segment, exist_ok=True)  # crea la carpeta si no existe
    # ruta_guardado = os.path.join(carpeta_salida_segment, nombre_archivo)
    # cv2.imwrite(ruta_guardado, recorte)

def is_plane(my_list):
    return all(not isinstance(x, (list, tuple, np.ndarray)) for x in my_list)

def process_frame(model_obb, model_ch, frame):
    angles_rotated_list = []
    characters_detected = True
    results = model_obb(frame, verbose=False)
    for result in results:
        rotated_image, angle_rotated, original_width, original_height = rotate(frame, result.obb)
        angles_rotated_list.append(angle_rotated)
        point_detection_attempts = 0
        while True:
            detected_characters = model_ch(rotated_image, verbose=False)
            hay_punto = (detected_characters[0].boxes.cls == 0).any().item()
            if not hay_punto:
                angle = 180 if point_detection_attempts == 0 else 90
                rotated_image = rotate_angle(rotated_image, angle)
                angles_rotated_list.append(angle)
                point_detection_attempts += 1
                if point_detection_attempts > 3:
                    # print(f"Sin detección válida en {nombre_archivo}")
                    characters_detected = False
                    break
            else:
                break
        
        if characters_detected:
            characters_coords = []
            xywh_list = detected_characters[0].boxes.xywh.squeeze().tolist()
            if is_plane(xywh_list):
                character_class = int(detected_characters[0].boxes.cls[0].item())
                character_conf = detected_characters[0].boxes.conf[0].item()
                characters_coords.append([xywh_list, character_class, character_conf])
            else:
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

            for i, ang in enumerate(reversed(angles_rotated_list)):
                annotated_img = rotate_angle(annotated_img, -ang)

            # Recortar la imagen
            current_height, current_width = annotated_img.shape[:2]
            start_x = (current_width - original_width) // 2
            start_y = (current_height - original_height) // 2
            end_x = start_x + original_width
            end_y = start_y + original_height

            # Recortar la región central
            cropped_image = annotated_img[start_y:end_y, start_x:end_x]

            return cropped_image, lectura
        
        else:
            return frame, "no detections"

