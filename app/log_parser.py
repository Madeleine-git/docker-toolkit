#!/usr/bin/env python3
"""
log_parser.py
=============
Módulo de análisis de logs SSH.

Mejoras aplicadas:
  01 - collections.Counter en lugar de diccionario manual
  02 - logging en lugar de print() para mensajes del sistema
"""

import os
from collections import Counter
from logger import configurar_logger


# ─── LOGGER DEL MÓDULO ───────────────────────────────────────
logger = configurar_logger("log_parser")


# ─── CONSTANTES ──────────────────────────────────────────────
RUTA_LOG: str      = "logs/auth.log"
PATRON_FALLO: str  = "Failed password"
UMBRAL_ATAQUES: int = 5


# ─── FUNCIÓN 1: PARSEAR EL LOG ───────────────────────────────

def parsear_log(ruta: str = RUTA_LOG) -> Counter[str]:
    """
    Lee auth.log línea a línea y cuenta intentos fallidos por IP.
    Usa Counter para contar y logging para mensajes del sistema.
    """

    if not os.path.exists(ruta):
        logger.error(f"No se encontró el fichero '{ruta}'")
        return Counter()

    ips_fallidas: list[str] = []

    logger.info(f"Iniciando análisis de {ruta}")

    with open(ruta, "r", encoding="utf-8") as fichero:
        for linea in fichero:
            linea = linea.strip()

            if PATRON_FALLO not in linea:
                continue

            partes: list[str] = linea.split()

            if len(partes) > 10 and "from" in partes:
                indice_from: int = partes.index("from")
                ip: str = partes[indice_from + 1]
                ips_fallidas.append(ip)

    conteo: Counter[str] = Counter(ips_fallidas)
    logger.info(f"Análisis completado: {len(conteo)} IPs únicas, {len(ips_fallidas)} intentos fallidos")

    return conteo


# ─── FUNCIÓN 2: IPs ÚNICAS ───────────────────────────────────

def obtener_ips_sospechosas(conteo: Counter[str]) -> set[str]:
    """Devuelve un Set con las IPs únicas que han fallado."""
    return set(conteo.keys())


# ─── FUNCIÓN 3: MOSTRAR REPORTE ──────────────────────────────

def mostrar_reporte(conteo: Counter[str]) -> None:
    """Muestra el reporte en pantalla. Usa print() para la UI."""

    if not conteo:
        print("\n  [INFO] No se encontraron intentos fallidos.")
        return

    ips_unicas: set[str] = obtener_ips_sospechosas(conteo)
    total_intentos: int = sum(conteo.values())
    ips_ordenadas = conteo.most_common()

    # La UI sigue usando print() — logging es para el sistema
    # print() es para el usuario, logging es para el servidor
    print("\n  " + "═" * 52)
    print("  REPORTE DE SEGURIDAD SSH")
    print("  " + "═" * 52)
    print(f"  IPs únicas atacantes:    {len(ips_unicas)}")
    print(f"  Total intentos fallidos: {total_intentos}")
    print(f"  Umbral de peligro:       ≥ {UMBRAL_ATAQUES} intentos")
    print("  " + "─" * 52)
    print(f"  {'IP':<20} {'Intentos':>10}   {'Estado'}")
    print("  " + "─" * 52)

    for ip, intentos in ips_ordenadas:
        if intentos >= UMBRAL_ATAQUES:
            estado: str = "⚠  PELIGROSA"
            logger.warning(f"IP peligrosa detectada: {ip} ({intentos} intentos)")
        else:
            estado = "●  Revisar"

        print(f"  {ip:<20} {intentos:>10}   {estado}")

    print("  " + "═" * 52)


# ─── MENÚ INTERACTIVO ────────────────────────────────────────

def menu_log_parser() -> None:
    """Submenú del módulo de análisis de logs SSH."""
    while True:
        print("\n  ── Analizador de logs SSH ──────────────────")
        print("  a.  Analizar auth.log y ver reporte")
        print("  b.  Ver solo IPs únicas detectadas")
        print("  v.  Volver al menú principal")
        print("  ────────────────────────────────────────────")

        opcion: str = input("\n  Elige una opción [a/b/v]: ").strip().lower()

        if opcion == "a":
            print(f"\n  Analizando {RUTA_LOG}...")
            conteo: Counter[str] = parsear_log()
            mostrar_reporte(conteo)

        elif opcion == "b":
            conteo_b: Counter[str] = parsear_log()
            ips: set[str] = obtener_ips_sospechosas(conteo_b)
            print(f"\n  IPs únicas que intentaron acceso: {len(ips)}")
            for ip in sorted(ips):
                print(f"    → {ip}")

        elif opcion == "v":
            break

        else:
            print("  [!] Opción no reconocida.")