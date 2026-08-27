from services import equipos_service, prestamos_service, usuarios_service


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

        match opcion:
            case "1":
                _mostrar_equipos()
            case "2":
                _crear_solicitud(usuario)
            case "3":
                propios = prestamos_service.listar_prestamos(usuario_id=usuario["id"])
                vigentes = [p for p in propios if p["estado"] in ("APROBADA", "ENTREGADA")]
                _mostrar_prestamos(vigentes, "Mis préstamos vigentes/futuros")
            case "4":
                atrasados = prestamos_service.listar_prestamos(usuario_id=usuario["id"], estado="ATRASADA")
                _mostrar_prestamos(atrasados, "Mis préstamos atrasados")
            case "5":
                _cancelar_solicitud(usuario)
            case "0":
                print("Sesión cerrada.")
                break
            case _:
                print("Opción inválida.")