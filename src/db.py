
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prestamos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('solicitante', 'encargado')),
    activo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_inventario TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    categoria TEXT,
    -- Aquí aplicamos tu regla de negocio de estados estrictos
    estado_fisico TEXT NOT NULL DEFAULT 'operativo' 
        CHECK (estado_fisico IN ('operativo', 'dañado', 'fuera de servicio')),
    activo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS prestamos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios (id),
    equipo_id INTEGER NOT NULL REFERENCES equipos (id),
    fecha_solicitud TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin_prevista TEXT NOT NULL,
    fecha_devolucion_real TEXT,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN (
            'PENDIENTE', 'APROBADA', 'RECHAZADA',
            'ENTREGADA', 'ATRASADA', 'DEVUELTA', 'CANCELADA'
        )),
    observaciones TEXT,
    motivo_rechazo TEXT,
    estado_recepcion TEXT,
    ubicacion TEXT
);
"""

def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database() -> None:
    conn = get_db_connection()
    conn.executescript(SCHEMA)
    conn.execute(
        "UPDATE equipos SET estado_fisico = 'operativo' WHERE estado_fisico IN ('bueno', 'regular')"
    )
    conn.commit()
    conn.close()
