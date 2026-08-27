
from services import equipos_service, prestamos_service, usuarios_service


def menu_encargado(usuario):
    while True:
            print(f"\n=== Menú Encargado ({usuario['nombre']}) ===")
            print("1. Registrar equipo")
            print("2. Registrar usuario")
            print("3. Ver catálogo de equipos")
            print("4. Registrar entrega de equipo")
            print("5. Registrar devolución de equipo (con estado de recepción)")
            print("6. Ver préstamos vigentes")
            print("7. Ver préstamos atrasados")
            print("0. Cerrar sesión")
    
            opcion = input("Seleccione una opción: ").strip()

            match opcion:
                case "1":
                    _registrar_equipo()
                case "2":
                    _registrar_usuario()
                case "3":
                    equipos = equipos_service.listar_equipos()
                    filas = [[e["id"], e["codigo_inventario"], e["nombre"], e["categoria"], e["estado_fisico"]] for e in equipos]
                    print(tabulate(filas, headers=["ID", "Código", "Nombre", "Categoría", "Estado físico"]))
                case "4":
                    _registrar_entrega()
                case "5":
                    _registrar_devolucion()
                case "6":
                    vigentes = prestamos_service.listar_prestamos()
                    vigentes = [p for p in vigentes if p["estado"] in ("APROBADA", "ENTREGADA")]
                    _mostrar_prestamos(vigentes, "Préstamos vigentes/futuros")
                case "7":
                    atrasados = prestamos_service.listar_prestamos(estado="ATRASADA")
                    _mostrar_prestamos(atrasados, "Préstamos atrasados")
                case "0":
                    print("Sesión cerrada.")
                    break
                case _:
                    print("Opción inválida.")