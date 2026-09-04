"""
Menú interactivo del rol Encargado.
"""

from tabulate import tabulate

from src.services import equipos_service, usuarios_service, prestamos_service


def _mostrar_prestamos(prestamos, titulo):
    print(f"\n--- {titulo} ---")
    if not prestamos:
        print("(sin registros)")
        return
    filas = [
        [p["id"], p["usuario_nombre"], p["equipo_nombre"], p["fecha_inicio"], p["fecha_fin_prevista"], p["estado"]]
        for p in prestamos
    ]
    print(tabulate(filas, headers=["ID", "Solicitante", "Equipo", "Inicio", "Fin previsto", "Estado"]))


def _registrar_equipo():
    codigo = input("Código de inventario: ").strip()
    nombre = input("Nombre del equipo: ").strip()
    categoria = input("Categoría: ").strip()
    ok, mensaje = equipos_service.crear_equipo(codigo, nombre, categoria)
    print(("✔ " if ok else "✘ ") + mensaje)


def _registrar_usuario():
    nombre = input("Nombre completo: ").strip()
    correo = input("Correo: ").strip()
    password = input("Contraseña temporal: ").strip()
    rol = input("Rol (solicitante/encargado): ").strip().lower()
    ok, mensaje = usuarios_service.crear_usuario(nombre, correo, password, rol)
    print(("✔ " if ok else "✘ ") + mensaje)


def _registrar_entrega():
    aprobadas = prestamos_service.listar_prestamos(estado="APROBADA")
    _mostrar_prestamos(aprobadas, "Préstamos aprobados, pendientes de entrega")
    if not aprobadas:
        return
    try:
        prestamo_id = int(input("ID del préstamo a entregar (0 para volver): ").strip())
    except ValueError:
        print("ID inválido.")
        return
    if prestamo_id == 0:
        return
    ok, mensaje = prestamos_service.registrar_entrega(prestamo_id)
    print(("✔ " if ok else "✘ ") + mensaje)


def _registrar_devolucion():
    entregados = prestamos_service.listar_prestamos(estado="ENTREGADA") + prestamos_service.listar_prestamos(estado="ATRASADA")
    _mostrar_prestamos(entregados, "Préstamos entregados / atrasados")
    if not entregados: return
    try:
        prestamo_id = int(input("ID del préstamo a devolver (0 para volver): ").strip())
    except ValueError:
        print("ID inválido.")
        return
    if prestamo_id == 0: return
    
    estados_permitidos = ["operativo", "dañado", "fuera de servicio"]
    estado_recepcion = ""
    while estado_recepcion not in estados_permitidos:
        estado_recepcion = input(f"Estado de recepción ({'/'.join(estados_permitidos)}): ").strip().lower()
        if estado_recepcion not in estados_permitidos:
            print("Error: Debe escribir exactamente una de las opciones permitidas.")
            
    observaciones = input("Observaciones adicionales (opcional): ").strip()
    ok, mensaje = prestamos_service.registrar_devolucion(prestamo_id, estado_recepcion, observaciones)
    print(("✔ " if ok else "✘ ") + mensaje)

def _gestionar_solicitudes():
    pendientes = prestamos_service.listar_prestamos(estado="PENDIENTE")
    _mostrar_prestamos(pendientes, "Solicitudes Pendientes de Aprobación")
    if not pendientes: return
    try:
        prestamo_id = int(input("ID de la solicitud (0 para volver): ").strip())
    except ValueError:
        return
    if prestamo_id == 0: return
    
    decision = input("¿Desea (A)probar o (R)echazar esta solicitud? ").strip().upper()
    if decision == 'A':
        ok, mensaje = prestamos_service.cambiar_estado(prestamo_id, "APROBADA")
    elif decision == 'R':
        ok, mensaje = prestamos_service.cambiar_estado(prestamo_id, "RECHAZADA")
    else:
        print("Opción inválida.")
        return
    print(("✔ " if ok else "✘ ") + mensaje)


def menu_encargado(usuario: dict):
    while True:
        print(f"\n=== Menú Encargado ({usuario['nombre']}) ===")
        print("1. Registrar equipo")
        print("2. Registrar usuario")
        print("3. Ver catálogo de equipos")
        print("4. Registrar entrega de equipo")
        print("5. Registrar devolución de equipo (con estado de recepción)")
        print("6. Gestionar solicitudes pendientes")
        print("7. Ver préstamos vigentes")
        print("8. Ver préstamos atrasados")
        print("0. Cerrar sesión")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            _registrar_equipo()
        elif opcion == "2":
            _registrar_usuario()
        elif opcion == "3":
            equipos = equipos_service.listar_equipos()
            filas = [[e["id"], e["codigo_inventario"], e["nombre"], e["categoria"], e["estado_fisico"]] for e in equipos]
            print(tabulate(filas, headers=["ID", "Código", "Nombre", "Categoría", "Estado físico"]))
        elif opcion == "4":
            _registrar_entrega()
        elif opcion == "5":
            _registrar_devolucion()
        elif opcion == "6":
            _gestionar_solicitudes()
        elif opcion == "7":
            vigentes = prestamos_service.listar_prestamos()
            vigentes = [p for p in vigentes if p["estado"] in ("APROBADA", "ENTREGADA")]
            _mostrar_prestamos(vigentes, "Préstamos vigentes/futuros")
        elif opcion == "8":
            atrasados = prestamos_service.listar_prestamos(estado="ATRASADA")
            _mostrar_prestamos(atrasados, "Préstamos atrasados")
        elif opcion == "0":
            print("Sesión cerrada.")
            break
        else:
            print("Opción inválida.")
