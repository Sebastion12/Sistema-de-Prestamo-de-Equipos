import json
import os


def cargar_datos(ruta):
    if not os.path.exists(ruta):
        guardar_datos(ruta, [])
        return []

    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()

        if not contenido:
            return []

        return json.loads(contenido)


def guardar_datos(ruta, datos):
    directorio = os.path.dirname(ruta)

    if directorio:
        os.makedirs(directorio, exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)