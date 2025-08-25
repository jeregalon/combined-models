import os
import numpy as np
import cv2

import cv2
import numpy as np

def rotate(image, coords):
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
        idx = (coords.cls == 0).nonzero(as_tuple=True)[0]
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

    M = cv2.getRotationMatrix2D((x, y), r, 1.0)
    rotated_image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    
    return rotated_image

def rotate_180(image):
    alto, ancho = image.shape[:2]
    x, y = ancho // 2, alto // 2
    M = cv2.getRotationMatrix2D((x, y), 180, 1.0)
    rotated_image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    
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

