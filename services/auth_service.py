
from storage import cargar_datos
import bcrypt
from logging_config import get_logger

logger = get_logger()

ARCHIVO_USUARIOS = "../data/usuarios.json"

def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(correo: str, password: str) -> dict | None:
    usuarios = cargar_datos(ARCHIVO_USUARIOS)

    usuario = next(
        (u for u in usuarios if u["correo"] == correo and u.get("activo", True)),
        None
    )

    if usuario is None:
        logger.info(f"Login fallido | correo={correo} | motivo=usuario no encontrado")
        return None

    if not verify_password(password, usuario["password_hash"]):
        logger.info(f"Login fallido | correo={correo} | motivo=contraseña incorrecta")
        return None

    logger.info(f"Login exitoso | correo={correo} | rol={usuario['rol']}")
    return usuario