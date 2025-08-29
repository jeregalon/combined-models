import os

def sincronize_labels(ruta):
    for nombre_archivo in os.listdir(ruta):
        # Solo procesar .txt
        if nombre_archivo.endswith(".txt") and len(nombre_archivo) > 8 + len(prefijo_constante):
            # Revisar si después de los 8 primeros caracteres viene el prefijo constante
            if nombre_archivo[8:].startswith(prefijo_constante):
                nuevo_nombre = nombre_archivo[8 + len(prefijo_constante):]
                ruta_antigua = os.path.join(ruta, nombre_archivo)
                ruta_nueva = os.path.join(ruta, nuevo_nombre)
                
                # Renombrar
                os.rename(ruta_antigua, ruta_nueva)
                print(f'Renombrado: "{nombre_archivo}" → "{nuevo_nombre}"')

def delete_leftover_images(ruta_txt, ruta_imgs):
    txt_nombres = {os.path.splitext(f)[0] for f in os.listdir(ruta_txt) if f.endswith(".txt")}
    for img in os.listdir(ruta_imgs):
        nombre_base, ext = os.path.splitext(img)
        if nombre_base not in txt_nombres:
            print(f"❌ No se encontró TXT para la imagen: '{img}'")
            ruta_img = os.path.join(ruta_imgs, img)
            os.remove(ruta_img)

# Ruta donde están los archivos
ruta_txt = r"data/labels"
ruta_imgs = r"data/images"

# Prefijo constante (después de los 8 primeros caracteres)
prefijo_constante = "__Digital%20Characters%20OBB%5C"

sincronize_labels(ruta_txt)

delete_leftover_images(ruta_txt, ruta_imgs)

