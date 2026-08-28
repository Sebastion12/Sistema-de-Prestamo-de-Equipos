"""
Menú interactivo del rol Solicitante.
"""

from tabulate import tabulate

from src.services import equipos_service, prestamos_service


def _mostrar_equipos():
    equipos = equipos_service.listar_equipos()
    if not equipos:
        print("No hay equipos registrados.")
        return
    filas = [[e["id"], e["codigo_inventario"], e["nombre"], e["categoria"], e["estado_fisico"]] for e in equipos]
    print(tabulate(filas, headers=["ID", "Código", "Nombre", "Categoría", "Estado físico"]))


def _mostrar_prestamos(prestamos, titulo):
    print(f"\n--- {titulo} ---")
    if not prestamos:
        print("(sin registros)")
        return
    filas = [
        [p["id"], p["equipo_nombre"], p["fecha_inicio"], p["fecha_fin_prevista"], p["estado"]]
        for p in prestamos
    ]
    print(tabulate(filas, headers=["ID", "Equipo", "Inicio", "Fin previsto", "Estado"]))


def _crear_solicitud(usuario):
    _mostrar_equipos()
    try:
        equipo_id = int(input("ID del equipo a solicitar: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    fecha_inicio = input("Fecha de inicio (AAAA-MM-DD): ").strip()
    fecha_fin = input("Fecha de fin prevista (AAAA-MM-DD): ").strip()
    ubicacion = input("Ubicación universitaria (opcional): ").strip()

    ok, mensaje = prestamos_service.crear_solicitud(
        usuario["id"], equipo_id, fecha_inicio, fecha_fin, ubicacion
    )
    # La solicitud se evalúa de inmediato (HD2): el resultado puede quedar "PENDIENTE" o "RECHAZADA" automáticamente
    print(("✔ " if ok else "✘ ") + mensaje)


def _cancelar_solicitud(usuario):
    mis_prestamos = prestamos_service.listar_prestamos(usuario_id=usuario["id"])
    activos = [p for p in mis_prestamos if p["estado"] == "APROBADA"]
    if not activos:
        print("No tiene solicitudes que se puedan cancelar.")
        return
    _mostrar_prestamos(activos, "Solicitudes cancelables")
    try:
        prestamo_id = int(input("ID de la solicitud a cancelar: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    ok, mensaje = prestamos_service.cancelar_solicitud(prestamo_id, usuario["id"])
    print(("✔ " if ok else "✘ ") + mensaje)


def menu_solicitante(usuario: dict):
    while True:
        print(f"\n=== Menú Solicitante ({usuario['nombre']}) ===")
        print("1. Ver catálogo de equipos")
        print("2. Solicitar préstamo de un equipo")
        print("3. Ver mis préstamos vigentes/futuros")
        print("4. Ver mis préstamos atrasados")
        print("5. Cancelar una solicitud")
        print("0. Cerrar sesión")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            _mostrar_equipos()
        elif opcion == "2":
            _crear_solicitud(usuario)
        elif opcion == "3":
            propios = prestamos_service.listar_prestamos(usuario_id=usuario["id"])
            vigentes = [p for p in propios if p["estado"] in ("APROBADA", "ENTREGADA")]
            _mostrar_prestamos(vigentes, "Mis préstamos vigentes/futuros")
        elif opcion == "4":
            atrasados = prestamos_service.listar_prestamos(usuario_id=usuario["id"], estado="ATRASADA")
            _mostrar_prestamos(atrasados, "Mis préstamos atrasados")
        elif opcion == "5":
            _cancelar_solicitud(usuario)
        elif opcion == "0":
            print("Sesión cerrada.")
            break
        else:
            print("Opción inválida.")
