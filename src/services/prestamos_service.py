import sqlite3
from datetime import datetime, timedelta, time
from src.db import get_db_connection
from src.logging_config import get_logger

logger = get_logger()

ESTADOS_ACTIVOS = ("PENDIENTE", "APROBADA", "ENTREGADA", "ATRASADA")
ESTADOS_RECEPCION = {"operativo", "dañado", "fuera de servicio"}
TRANSICIONES_VALIDAS = {
    "PENDIENTE": {"APROBADA", "RECHAZADA"},
    "APROBADA": {"ENTREGADA", "CANCELADA"},
    "ENTREGADA": {"DEVUELTA"},
    "ATRASADA": {"DEVUELTA"},
}
HORA_RETIRO = time(9, 0)

def _calcular_dias_habiles(fecha_inicio: datetime, fecha_fin: datetime) -> int:
    # Guardia contra rangos absurdos antes de iterar día a día (el bug #3 que vimos antes)
    if (fecha_fin - fecha_inicio).days > 60:
        return (fecha_fin - fecha_inicio).days  # ya es > 7 hábiles seguro; se rechaza más abajo

    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual.strftime("%Y-%m-%d"):
            dias += 1
        actual += timedelta(days=1)
    return dias

def crear_solicitud(usuario_id: int, equipo_id: int, fecha_inicio_str: str, fecha_fin_str: str, ubicacion: str) -> tuple[bool, str]:
    conn = get_db_connection()
    try:
        usuario = conn.execute(
            "SELECT 1 FROM usuarios WHERE id = ? AND activo = 1", (usuario_id,)
        ).fetchone()
        if usuario is None:
            return False, "El usuario no existe o está inactivo."

        # Regla 1: Validar formato y fechas (Mínimo 24 hrs)
        try:
            inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
        except ValueError:
            return False, "Formato de fecha inválido. Use AAAA-MM-DD."

        if fin < inicio:
            return False, "La fecha de fin debe ser posterior o igual a la fecha de inicio."
            
        inicio_con_hora = datetime.combine(inicio.date(), HORA_RETIRO)
        if inicio_con_hora < datetime.now() + timedelta(hours=24):
            return False, "Las solicitudes deben hacerse con al menos 24 horas de anticipación a la hora de retiro (09:00)."
            
        # Regla 2: Máximo 7 días hábiles
        if _calcular_dias_habiles(inicio, fin) > 7:
            return False, "El préstamo no puede superar los 7 días hábiles."

        # Regla 3: Límite de 5 equipos por persona
        cursor = conn.execute(
            "SELECT COUNT(*) as total FROM prestamos WHERE usuario_id = ? AND estado IN (?, ?, ?, ?)",
            (usuario_id, *ESTADOS_ACTIVOS)
        )
        if cursor.fetchone()['total'] >= 5:
            return False, "Ha alcanzado el límite máximo de 5 equipos en préstamo/solicitados."

        equipo = conn.execute(
            "SELECT estado_fisico FROM equipos WHERE id = ? AND activo = 1", (equipo_id,)
        ).fetchone()
        if equipo is None:
            return False, "El equipo no existe o está inactivo."
        if equipo["estado_fisico"] != "operativo":
            return False, "El equipo no está disponible porque no se encuentra operativo."

        ocupado = conn.execute(
            """
            SELECT 1 FROM prestamos
            WHERE equipo_id = ? AND estado IN (?, ?, ?, ?)
              AND fecha_inicio <= ? AND fecha_fin_prevista >= ?
            LIMIT 1
            """,
            (equipo_id, *ESTADOS_ACTIVOS, fecha_fin_str, fecha_inicio_str),
        ).fetchone()
        if ocupado is not None:
            return False, "El equipo ya está reservado durante esas fechas."

        # Si pasa todas las validaciones, se crea como PENDIENTE (Soluciona el Bug del Flujo)
        conn.execute(
            "INSERT INTO prestamos (usuario_id, equipo_id, fecha_solicitud, fecha_inicio, fecha_fin_prevista, estado, ubicacion) VALUES (?, ?, ?, ?, ?, 'PENDIENTE', ?)",
            (usuario_id, equipo_id, datetime.now().strftime("%Y-%m-%d"), fecha_inicio_str, fecha_fin_str, ubicacion)
        )
        conn.commit()
        logger.info(f"Solicitud PENDIENTE creada | usuario={usuario_id} | equipo={equipo_id}")
        return True, "Solicitud creada exitosamente. Queda pendiente de aprobación."
        
    finally:
        conn.close()

# Función de apoyo para el menú encargado
def cambiar_estado(prestamo_id: int, nuevo_estado: str) -> tuple[bool, str]:
    if nuevo_estado not in {"APROBADA", "RECHAZADA", "ENTREGADA", "CANCELADA"}:
        return False, "Estado nuevo inválido."
    conn = get_db_connection()
    try:
        prestamo = conn.execute("SELECT estado FROM prestamos WHERE id = ?", (prestamo_id,)).fetchone()
        if prestamo is None:
            return False, "El préstamo no existe."
        if nuevo_estado not in TRANSICIONES_VALIDAS.get(prestamo["estado"], set()):
            return False, f"No se puede cambiar de {prestamo['estado']} a {nuevo_estado}."
        conn.execute("UPDATE prestamos SET estado = ? WHERE id = ?", (nuevo_estado, prestamo_id))
        conn.commit()
        logger.info(f"Cambio de estado | prestamo={prestamo_id} | estado={nuevo_estado}")
        return True, f"Solicitud marcada como {nuevo_estado}."
    finally:
        conn.close()

def listar_prestamos(usuario_id: int = None, estado: str = None) -> list[dict]:
    conn = get_db_connection()
    try:
        # Hacemos un JOIN para traer los nombres reales del usuario y del equipo, no solo sus IDs
        query = """
            SELECT p.*, u.nombre as usuario_nombre, e.nombre as equipo_nombre 
            FROM prestamos p
            JOIN usuarios u ON p.usuario_id = u.id
            JOIN equipos e ON p.equipo_id = e.id
            WHERE 1=1
        """
        params = []
        if usuario_id:
            query += " AND p.usuario_id = ?"
            params.append(usuario_id)
        if estado:
            query += " AND p.estado = ?"
            params.append(estado)
            
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def cancelar_solicitud(prestamo_id: int, usuario_id: int | None = None) -> tuple[bool, str]:
    conn = get_db_connection()
    try:
        prestamo = conn.execute("SELECT usuario_id, estado FROM prestamos WHERE id = ?", (prestamo_id,)).fetchone()
        if prestamo is None:
            return False, "El préstamo no existe."
        if usuario_id is not None and prestamo["usuario_id"] != usuario_id:
            return False, "No puede cancelar una solicitud de otro usuario."
        if prestamo["estado"] not in {"PENDIENTE", "APROBADA"}:
            return False, "Solo se pueden cancelar solicitudes pendientes o aprobadas."
        conn.execute("UPDATE prestamos SET estado = 'CANCELADA' WHERE id = ?", (prestamo_id,))
        conn.commit()
        logger.info(f"Solicitud cancelada | prestamo={prestamo_id}")
        return True, "Solicitud cancelada exitosamente."
    finally:
        conn.close()

def registrar_entrega(prestamo_id: int) -> tuple[bool, str]:
    return cambiar_estado(prestamo_id, "ENTREGADA")

def registrar_devolucion(prestamo_id: int, estado_recepcion: str, observaciones: str) -> tuple[bool, str]:
    estado_recepcion = estado_recepcion.strip().lower()
    if estado_recepcion not in ESTADOS_RECEPCION:
        return False, "Estado de recepción inválido. Use 'operativo', 'dañado' o 'fuera de servicio'."

    conn = get_db_connection()
    try:
        prestamo = conn.execute(
            "SELECT equipo_id, estado FROM prestamos WHERE id = ?", (prestamo_id,)
        ).fetchone()
        if prestamo is None:
            return False, "El préstamo no existe."
        if prestamo["estado"] not in {"ENTREGADA", "ATRASADA"}:
            return False, "Solo se pueden devolver préstamos entregados o atrasados."

        # Actualizamos el préstamo
        conn.execute(
            "UPDATE prestamos SET estado = 'DEVUELTA', estado_recepcion = ?, observaciones = ?, fecha_devolucion_real = ? WHERE id = ?",
            (estado_recepcion, observaciones, datetime.now().strftime("%Y-%m-%d"), prestamo_id)
        )
        
        # Obtenemos el ID del equipo asociado a este préstamo para actualizar su estado físico
        equipo_id = prestamo["equipo_id"]
        conn.execute("UPDATE equipos SET estado_fisico = ? WHERE id = ?", (estado_recepcion, equipo_id))
        
        conn.commit()
        logger.info(f"Devolución registrada | prestamo={prestamo_id} | estado_equipo={estado_recepcion}")
        return True, "Devolución registrada correctamente."
    finally:
        conn.close()