import sqlite3
from src.db import get_db_connection
from src.logging_config import get_logger

logger = get_logger()

def crear_equipo(codigo_inventario: str, nombre: str, categoria: str) -> tuple[bool, str]:
    codigo_inventario = codigo_inventario.strip()
    nombre = nombre.strip()
    categoria = categoria.strip()
    if not codigo_inventario or not nombre:
        return False, "El código de inventario y el nombre son obligatorios."

    conn = get_db_connection()
    try:
        # Nota: 'estado_fisico' tomará automáticamente el valor 'operativo' que definiste en db.py
        conn.execute(
            "INSERT INTO equipos (codigo_inventario, nombre, categoria) VALUES (?, ?, ?)",
            (codigo_inventario, nombre, categoria)
        )
        conn.commit()
        logger.info(f"Equipo creado | codigo={codigo_inventario} | nombre={nombre}")
        return True, "Equipo registrado correctamente."
    except sqlite3.IntegrityError:
        return False, f"Ya existe un equipo con el código '{codigo_inventario}'."
    finally:
        conn.close()

def listar_equipos() -> list[dict]:
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM equipos WHERE activo = 1")
        # Convertimos las filas de SQLite a diccionarios de Python para que tabulate los lea bien
        equipos = [dict(row) for row in cursor.fetchall()]
        return equipos
    finally:
        conn.close()