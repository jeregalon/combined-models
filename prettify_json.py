import json
import sys

def prettify_json(input_file, output_file):
    # Abrimos el archivo JSON original
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)  # Esto convierte la línea JSON en un objeto de Python

    # Guardamos el JSON ya formateado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # indent=4 agrega la indentación

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python format_json.py archivo_entrada.json archivo_salida.json")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        prettify_json(input_file, output_file)
        print(f"Archivo formateado guardado en {output_file}")
