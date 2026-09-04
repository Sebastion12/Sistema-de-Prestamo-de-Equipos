
from src.db import get_db_connection, initialize_database
from src.services import usuarios_service, equipos_service


def _base_vacia() -> bool:
    conn = get_db_connection()
    row = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()
    conn.close()
    return row["total"] == 0


def _equipos_vacios() -> bool:
    conn = get_db_connection()
    row = conn.execute("SELECT COUNT(*) AS total FROM equipos").fetchone()
    conn.close()
    return row["total"] == 0


def cargar_datos_demo():
    initialize_database()
    if _base_vacia():
        usuarios_service.crear_usuario("Admin", "admin.encargado@usm.cl", "encargado123", "encargado")
        usuarios_service.crear_usuario("user", "user.solicitante@usm.cl", "solicitante123", "solicitante")

    if _equipos_vacios():
        equipos_service.crear_equipo("NB-001", "Notebook Dell Latitude", "Notebook")
        equipos_service.crear_equipo("NB-002", "Notebook Lenovo ThinkPad", "Notebook")
        equipos_service.crear_equipo("PR-001", "Proyector Epson", "Proyector")
        equipos_service.crear_equipo("CM-001", "Cámara Canon EOS", "Cámara")
        equipos_service.crear_equipo("CM-002", "Cámara Canon HD", "Cámara")
        equipos_service.crear_equipo("CM-003", "Cámara Canon XD", "Cámara")
    
    print("Datos de demostración cargados:")
    print("  Encargado -> correo: admin.encargado@usm.cl | password: encargado123")
    print("  Solicitante -> correo: user.solicitante@usm.cl | password: solicitante123")



if __name__ == "__main__":
    cargar_datos_demo()
