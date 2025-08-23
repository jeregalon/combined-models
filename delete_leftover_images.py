import os

# def sincronizar_nombres(ruta_txt, ruta_imgs):
#     # Obtener nombres de TXT (sin extensión)
#     txt_nombres = {os.path.splitext(f)[0] for f in os.listdir(ruta_txt) if f.endswith(".txt")}

#     for img in os.listdir(ruta_imgs):
#         nombre_base, ext = os.path.splitext(img)

#         # Reemplazos manuales
#         nombre_corregido = (nombre_base
#                             .replace(" ", "%20")
#                             .replace("(", "%28")
#                             .replace(")", "%29"))

#         # Verificar si existe TXT correspondiente
#         if nombre_corregido in txt_nombres:
#             origen = os.path.join(ruta_imgs, img)
#             destino = os.path.join(ruta_imgs, nombre_corregido + ext)
#             if origen != destino:  # Evitar renombrar si ya es igual
#                 os.rename(origen, destino)
#                 print(f'✅ Renombrado: "{img}" → "{nombre_corregido + ext}"')

#     print("\n🎉 Todas las imágenes tienen TXT correspondiente y han sido renombradas.")


def borrar_faltantes(ruta_txt, ruta_imgs):
    txt_nombres = {os.path.splitext(f)[0] for f in os.listdir(ruta_txt) if f.endswith(".txt")}
    for img in os.listdir(ruta_imgs):
        nombre_base, ext = os.path.splitext(img)
        if nombre_base not in txt_nombres:
            print(f"❌ No se encontró TXT para la imagen: '{img}'")
            ruta_img = os.path.join(ruta_imgs, img)
            os.remove(ruta_img)


# Ejemplo de uso
ruta_txt = r"data/labels"
ruta_imgs = r"data/images"

borrar_faltantes(ruta_txt, ruta_imgs)
