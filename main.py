from src.db import initialize_database
from src.auth import login
from src.menu_encargado import menu_encargado
from src.menu_solicitante import menu_solicitante
from src.demo_data import cargar_datos_demo
import sentry_sdk

sentry_sdk.init(
    dsn="https://f72981bac0257774d45a9abd45b1fbf8@o4511986147590144.ingest.de.sentry.io/4511986156306512",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

def pantalla_login():
    print("\n--- Sistema de Prestamo de equipos ---")
    correo = input("Ingrese su correo electrónico: ").strip()
    password = input("Ingrese su password/contraseña: ").strip()
    usuario = login(correo, password)
    if usuario is None:
        print("Correo o contraseña incorrectos. Intente nuevamente.")
        return None

    print(f"Bienvenido, {usuario['nombre']}! Rol: {usuario['rol']}")
    return usuario



def main():
    initialize_database()
    cargar_datos_demo()  # Carga de datos de demostración
    

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