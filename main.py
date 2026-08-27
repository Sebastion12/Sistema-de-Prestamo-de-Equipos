
from menus import menu_encargado, menu_solicitante

def pantalla_login():
    correo = input("Ingrese su correo electrónico: ").strip()
    password = input("Ingrese su password/contraseña: ").strip()

    usuario = login(correo, password)

    if usuario is None:
        print("Correo o contraseña incorrectos. Intente nuevamente.")
        return None

    print(f"Bienvenido, {usuario['nombre']}! Rol: {usuario['rol']}")
    return usuario

def main():
    print("Sistema de Préstamo de Equipos")

    while True:
        usuario = pantalla_login()

        if usuario is None:
            reintentar = input("¿Desea intentar iniciar sesión nuevamente? (s/n): ")
            if reintentar.lower() != "s":
                break
            continue

        if usuario["rol"] == "encargado":
            menu_encargado(usuario)
        else:
            menu_solicitante(usuario)

        continuar = input("¿Volver a la pantalla de login? (s/n): ").strip().lower()
        if continuar.lower() != "s":
            break


if __name__ == "__main__":
    main()
