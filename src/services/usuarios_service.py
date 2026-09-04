import sqlite3

from src.db import get_db_connection
from src.auth import hash_password
from src.logging_config import get_logger

logger = get_logger()


def crear_usuario(nombre: str, correo: str, password: str, rol: str) -> tuple[bool, str]:
    if rol not in ("solicitante", "encargado"):
        return False, "Rol inválido. Debe ser 'solicitante' o 'encargado'."
    if not nombre.strip() or not correo.strip() or not password:
        return False, "Nombre, correo y contraseña son obligatorios."
    if not correo.strip().lower().endswith("@usm.cl"):
        return False, f"El correo debe pertenecer al dominio institucional @usm.cl"

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO usuarios (nombre, correo, password_hash, rol) VALUES (?, ?, ?, ?)",
            (nombre.strip(), correo.strip().lower(), hash_password(password), rol),
        )
        conn.commit()
        logger.info(f"Usuario creado | correo={correo} | rol={rol}")
        return True, "Usuario creado correctamente."
    except sqlite3.IntegrityError:
        return False, "Ya existe un usuario registrado con ese correo."
    finally:
        conn.close()