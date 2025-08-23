import os

# Ruta donde están los archivos
ruta = r"data/labels"

# Prefijo constante (después de los 8 primeros caracteres)
prefijo_constante = "__Digital%20Characters%5C"

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
