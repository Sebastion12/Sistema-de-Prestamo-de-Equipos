
from src.logging_config import get_logger
from src.db import get_db_connection
import bcrypt

logger = get_logger()

def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(correo:str, password:str) -> dict | None:

    conn = get_db_connection()

    row = conn.execute(
        "SELECT * FROM usuarios WHERE correo = ? AND activo = 1", (correo,)
    ).fetchone()
    conn.close()

    if row is None:
        logger.info(f"Login fallido | correo={correo} | motivo=usuario no encontrado")
        return None
    
    if not verify_password(password, row['password_hash']):
        logger.info(f"Login fallido | correo={correo} | motivo=contraseña incorrecta")
        return None

    logger.info(f"Login exitoso | correo={correo} | rol={row['rol']}")
    return dict(row)
    