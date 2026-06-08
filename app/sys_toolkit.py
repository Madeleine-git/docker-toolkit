#!/usr/bin/env python3
"""
sys_toolkit.py
Kit de herramientas para administradores de sistemas.
Menú interactivo CLI.
"""
import network_models
import os_utils
import log_parser
import threat_intel
import inventory_manager
import report_generator
import sys

# ── CONSTANTES ───────────────────────────────────────────
# Las constantes van en MAYÚSCULAS por convención.
# ': str' es un Type Hint — le dice a Python que es texto.
VERSION: str = "1.0.0"
APP_NAME: str = "SysAdmin Toolkit"


# ── FUNCIONES ────────────────────────────────────────────
# '-> None' significa que la función no devuelve ningún valor,
# solo ejecuta acciones como imprimir en pantalla.

def mostrar_banner() -> None:
    """Muestra el banner de bienvenida. Se llama UNA sola vez."""
    print("=" * 50)
    print(f"  {APP_NAME}  v{VERSION}")
    print("  Herramientas para administradores de sistemas")
    print("=" * 50)
    print()


def mostrar_menu() -> None:
    print("\n─── MENÚ PRINCIPAL ───────────────────────────")
    print("  1.  Automatización del sistema operativo")
    print("  2.  Auditor de seguridad SSH")
    print("  3.  Analizador de logs SSH")
    print("  4.  Modelos de red (POO)")
    print("  5.  Inteligencia de amenazas (API)")
    print("  6.  Gestión de inventarios")
    print("  7.  Generador de informes Excel")
    print("  8.  Geolocalizador de IPs sospechosas")
    print("  9.  Acerca de este toolkit")
    print("  0.  Salir")
    print("──────────────────────────────────────────────")

def mostrar_info() -> None:
    """Muestra información sobre el toolkit."""
    print("\n  [INFO] Proyecto: SysAdmin Toolkit")
    print(f"  [INFO] Versión:  {VERSION}")
    print("  [INFO] Módulos:  SSH Auditor | CSV→Excel | GeoIP")


def ejecutar_os_utils() -> None:
    """Módulo 2 – Automatización del sistema operativo."""
    os_utils.menu_os_utils()


def ejecutar_auditor_ssh() -> None:
    """Módulo 1 – Auditor SSH (se implementa en el paso 2)."""
    print("\n  [MÓDULO 1] Auditor SSH")
    print("  ► Próximamente: análisis de auth.log")


def ejecutar_log_parser() -> None:
    """Módulo 3 – Analizador de logs SSH."""
    log_parser.menu_log_parser()


def ejecutar_network_models() -> None:
    """Módulo 4 – Modelos de red con POO."""
    network_models.menu_network_models()


def ejecutar_threat_intel() -> None:
    """Módulo 5 – Inteligencia de amenazas."""
    threat_intel.menu_threat_intel()
    

def ejecutar_inventory_manager() -> None:
    """Módulo 6 – Gestión de inventarios."""
    inventory_manager.menu_inventory_manager()


def ejecutar_report_generator() -> None:
    """Módulo 7 – Generador de informes Excel."""
    report_generator.menu_report_generator()


def ejecutar_procesador_csv() -> None:
    """Módulo 2 – CSV → Excel (se implementa en el paso 3)."""
    print("\n  [MÓDULO 2] Procesador de inventario")
    print("  ► Próximamente: CSV a Excel con pandas")


def ejecutar_geoip() -> None:
    """Módulo 3 – Geolocalizador de IPs (se implementa en el paso 4)."""
    print("\n  [MÓDULO 3] Geolocalizador de IPs")
    print("  ► Próximamente: consulta a ip-api.com")


def main() -> None:
    """
    Función principal con el bucle del menú.

    CONCEPTOS:
      while True  → bucle infinito, se repite hasta sys.exit()
      input()     → pausa y espera texto del usuario (siempre str)
      .strip()    → elimina espacios accidentales
      sys.exit(0) → termina el programa limpiamente
    """
    mostrar_banner()

    while True:
        mostrar_menu()

        # input() SIEMPRE devuelve str
        # por eso comparamos con "1" y no con el número 1
        opcion: str = input("\n  Elige una opción [0-9]: ").strip()

        if opcion == "1":
            ejecutar_os_utils()

        elif opcion == "2":
            ejecutar_auditor_ssh()

        elif opcion == "3":
            ejecutar_log_parser()

        elif opcion == "4":
            ejecutar_network_models()

        elif opcion == "5":
            ejecutar_threat_intel()

        elif opcion == "6":
            ejecutar_inventory_manager()

        elif opcion == "7":
            ejecutar_report_generator()

        elif opcion == "8":
            ejecutar_geoip()

        elif opcion == "9":
            mostrar_info()

        elif opcion == "0":
            print("\n  Hasta pronto. Cerrando el toolkit...\n")
            sys.exit(0)

        else:
            print(f"\n  [!] Opción '{opcion}' no reconocida. Intenta de nuevo.")
# Solo arranca main() si ejecutas ESTE fichero directamente
if __name__ == "__main__":
    main()