import json
import os
import urllib.parse
import numpy as np

def labelstudio_to_yoloobb(json_file, output_dir):
    with open(json_file, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    for item in data_list:
        # Nombre de la imagen desde "data/image"
        image_path = item.get('data', {}).get('image', '')
        if not image_path:
            continue

        # Extraemos solo el nombre de archivo, eliminando prefijo
        image_name = os.path.basename(urllib.parse.unquote(image_path))
        txt_name = os.path.splitext(image_name)[0] + ".txt"
        txt_name_corregido = (txt_name
                            .replace(" ", "%20")
                            .replace("(", "%28")
                            .replace(")", "%29"))
        output_path = os.path.join(output_dir, txt_name_corregido)

        annotations = item.get('annotations', [])
        results = annotations[0].get('result', [])

        lines = []

        for obj in results:
            value = obj.get('value', {})
            rect_labels = value.get('rectanglelabels', [])
            if not rect_labels:
                continue

            # Coordenadas del JSON
            x2_t = value['x']
            y2_t = value['y']
            width = value['width']
            height = value['height']
            angle = value.get('rotation', 0)

            # Coordenadas de las esquinas de la caja delimitadora
            x1 = width
            y1 = 0

            x2 = 0
            y2 = 0

            x3 = 0
            y3 = height

            x4 = width
            y4 = height

            # Convertir el ángulo a radianes
            angle_in_rad = np.radians(angle)

            # Matriz de rotación
            rot_matrix = np.array([
                [np.cos(angle_in_rad), -np.sin(angle_in_rad)],
                [np.sin(angle_in_rad), np.cos(angle_in_rad)]
            ])

            # Calcular coordenadas rotadas
            x1_rot, y1_rot = rot_matrix @ np.array([x1, y1])
            x2_rot, y2_rot = rot_matrix @ np.array([x2, y2])
            x3_rot, y3_rot = rot_matrix @ np.array([x3, y3])
            x4_rot, y4_rot = rot_matrix @ np.array([x4, y4])

            # Trasladar
            x1 = x1_rot + x2_t
            y1 = y1_rot + y2_t

            x2 = x2_t
            y2 = y2_t

            x3 = x3_rot + x2_t
            y3 = y3_rot + y2_t

            x4 = x4_rot + x2_t
            y4 = y4_rot + y2_t

            # Normalizar
            x1 /= 100
            y1 /= 100

            x2 /= 100
            y2 /= 100

            x3 /= 100
            y3 /= 100

            x4 /= 100
            y4 /= 100

            # Usamos la primera etiqueta como class_id (puedes mapear a ID real si quieres)
            class_id = 0

            lines.append(f"{class_id} {x2:.16f} {y2:.16f} {x1:.16f} {y1:.16f} {x4:.16f} {y4:.16f} {x3:.16f} {y3:.16f}")

        # Escribimos solo si hay líneas
        if lines:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write("\n".join(lines))

    print(f"Conversión completada. Archivos guardados en {output_dir}")

# Ejemplo de uso
if __name__ == "__main__":
    labelstudio_to_yoloobb("dataset_formateado.json", "yoloobb_labels")
