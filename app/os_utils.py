#!/usr/bin/env python3
"""
os_utils.py
===========
Módulo de automatización del sistema operativo.

Herramientas:
  - check_ping(ip)         → comprueba si una IP responde
  - check_disk(ruta)       → comprueba el espacio libre en disco

Librerías usadas:
  - subprocess  → ejecutar comandos del sistema operativo
  - os          → detectar el sistema operativo actual
  - shutil      → obtener estadísticas del disco
"""

import subprocess
import os
import shutil


# ─── CONSTANTES ──────────────────────────────────────────────
# Umbral mínimo de espacio libre en disco.
# Si el espacio libre baja de este porcentaje → alerta.
UMBRAL_DISCO: int = 20 # porcentaje


# ─── FUNCIÓN 1: PING ─────────────────────────────────────────

def check_ping(ip: str) -> bool:
    """
    Comprueba si una IP responde a ping.

    Parámetros:
      ip (str) → la dirección IP a comprobar. Ejemplo: "8.8.8.8"

    Devuelve:
      True  → la IP responde (dispositivo encendido y accesible)
      False → la IP no responde (apagado, caído o bloqueado)

    CONCEPTO — subprocess.run():
      Ejecuta un comando del sistema operativo desde Python.
      Es exactamente igual que escribirlo en la terminal,
      pero controlado desde tu script.

    CONCEPTO — returncode:
      Cuando un comando termina, devuelve un número:
        0  = éxito (el ping llegó y recibió respuesta)
        1  = fallo (no hubo respuesta)
      Comparamos con 0 para saber si funcionó.
    """

    # Detectamos el sistema operativo para usar el comando correcto
    # os.name vale 'nt' en Windows y 'posix' en Linux/Mac
    if os.name == "nt":
        # Windows: ping -n 1 (envía 1 paquete)
        comando: list[str] = ["ping", "-n", "1", ip]
    else:
        # Linux/Mac: ping -c 1 (envía 1 paquete)
        comando = ["ping", "-c", "1", ip]

    try:
        resultado = subprocess.run(
            comando,
            stdout=subprocess.DEVNULL,  # oculta la salida del ping
            stderr=subprocess.DEVNULL,  # oculta los errores
            timeout=5                   # espera máximo 5 segundos
        )
        # Si returncode es 0 → éxito → devolvemos True
        return resultado.returncode == 0

    except subprocess.TimeoutExpired:
        # El ping tardó más de 5 segundos → consideramos caído
        print(f"  [!] Timeout: {ip} no respondió en 5 segundos.")
        return False

    except Exception as e:
        # Cualquier otro error inesperado
        print(f"  [!] Error al hacer ping a {ip}: {e}")
        return False


# ─── FUNCIÓN 2: ESPACIO EN DISCO ─────────────────────────────

def check_disk(ruta: str = "C:\\") -> None:
    """
    Comprueba el espacio libre en disco de una ruta dada
    y lanza una alerta si está por debajo del umbral.

    Parámetros:
      ruta (str) → partición a analizar.
                   Windows: "C:\\"  Linux: "/"
                   Por defecto analiza C:\\ en Windows.

    CONCEPTO — shutil.disk_usage():
      Devuelve tres valores: total, used, free (en bytes).
      Los bytes los convertimos a GB dividiendo entre
      1024 * 1024 * 1024.

    CONCEPTO — valor por defecto en parámetros:
      'ruta: str = "C:\\"' significa que si llamas a
      check_disk() sin argumentos, usará "C:\\" por defecto.
      Pero puedes cambiarlo: check_disk("D:\\")
    """

    try:
        # Obtenemos las estadísticas del disco
        uso = shutil.disk_usage(ruta)

        # Convertimos bytes a gigabytes (más legible)
        total_gb: float = uso.total / (1024 ** 3)
        libre_gb: float = uso.free  / (1024 ** 3)
        usado_gb: float = uso.used  / (1024 ** 3)

        # Calculamos el porcentaje libre
        porcentaje_libre: float = (uso.free / uso.total) * 100
        porcentaje_usado: float = 100 - porcentaje_libre

        # Mostramos el reporte
        print(f"\n  {'─' * 40}")
        print(f"  REPORTE DE DISCO: {ruta}")
        print(f"  {'─' * 40}")
        print(f"  Total:      {total_gb:.1f} GB")
        print(f"  Usado:      {usado_gb:.1f} GB  ({porcentaje_usado:.1f}%)")
        print(f"  Libre:      {libre_gb:.1f} GB  ({porcentaje_libre:.1f}%)")

        # Barra visual de uso del disco
        bloques_usados: int = int(porcentaje_usado / 5)
        bloques_libres: int = 20 - bloques_usados
        barra: str = "█" * bloques_usados + "░" * bloques_libres
        print(f"  [{barra}] {porcentaje_usado:.1f}%")
        print(f"  {'─' * 40}")

        # Comprobamos si estamos por debajo del umbral
        if porcentaje_libre < UMBRAL_DISCO:
            print(f"  ⚠  ALERTA: Espacio libre por debajo del {UMBRAL_DISCO}%")
            print(f"  ⚠  Considera liberar espacio en {ruta}")
        else:
            print(f"  ✓  Espacio en disco: OK (>{UMBRAL_DISCO}% libre)")

    except FileNotFoundError:
        print(f"  [!] Error: la ruta '{ruta}' no existe.")
    except Exception as e:
        print(f"  [!] Error al analizar el disco: {e}")


# ─── FUNCIÓN INTERACTIVA: MENÚ DEL MÓDULO ────────────────────

def menu_os_utils() -> None:
    """
    Submenú interactivo del módulo de automatización.
    Se llama desde el menú principal de sys_toolkit.py.
    """
    while True:
        print("\n  ── Automatización del sistema operativo ──")
        print("  a.  Hacer ping a una IP")
        print("  b.  Comprobar espacio en disco")
        print("  v.  Volver al menú principal")
        print("  ─────────────────────────────────────────")

        opcion: str = input("\n  Elige una opción [a/b/v]: ").strip().lower()

        if opcion == "a":
            ip: str = input("\n  Introduce la IP a comprobar: ").strip()
            print(f"\n  Haciendo ping a {ip}...")
            if check_ping(ip):
                print(f"  ✓  {ip} está ACTIVA y responde.")
            else:
                print(f"  ✗  {ip} NO responde o está caída.")

        elif opcion == "b":
            print("\n  Ruta por defecto: C:\\")
            ruta_input: str = input(
                "  Introduce otra ruta o pulsa Enter para usar C:\\: "
            ).strip()
            ruta: str = ruta_input if ruta_input else "C:\\"
            check_disk(ruta)

        elif opcion == "v":
            break  # sale del bucle y vuelve al menú principal

        else:
            print("  [!] Opción no reconocida.")