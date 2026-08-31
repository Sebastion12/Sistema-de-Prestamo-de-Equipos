"""
Configuración de logging de eventos relevantes del sistema
(creación de solicitudes, cambios de estado, errores, etc.).
"""

import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "app.log"


def get_logger() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("prestamo_equipos")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(file_handler)

    return logger
