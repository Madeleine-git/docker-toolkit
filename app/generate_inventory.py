#!/usr/bin/env python3
"""
generate_inventory.py
=====================
Genera un inventario ficticio de 1000 servidores y lo guarda en data/inventory.csv.

Librerías:
  - csv    → escribir el fichero CSV
  - random → elegir valores aleatorios
  - faker  → generar datos ficticios realistas
"""

import csv
import random
from faker import Faker


# ─── CONSTANTES ──────────────────────────────────────────────
RUTA_CSV: str = "data/inventory.csv"
TOTAL_SERVIDORES: int = 1000

# Datos realistas para generar el inventario
SISTEMAS_OPERATIVOS: list[str] = [
    "Windows Server 2019",
    "Windows Server 2022",
    "Ubuntu 20.04 LTS",
    "Ubuntu 22.04 LTS",
    "CentOS 7",
    "Red Hat Enterprise Linux 8",
    "Debian 11"
]

DEPARTAMENTOS: list[str] = [
    "Infraestructura",
    "Desarrollo",
    "Base de Datos",
    "Seguridad",
    "Redes",
    "RRHH",
    "Finanzas",
    "Operaciones"
]

ROLES: list[str] = [
    "Web Server",
    "Database Server",
    "File Server",
    "Mail Server",
    "DNS Server",
    "Backup Server",
    "Monitoring Server",
    "Application Server"
]

RAM_OPCIONES: list[int] = [2, 4, 8, 16, 32, 64, 128]

ESTADOS: list[str] = ["Activo", "Mantenimiento", "Apagado"]


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────

def generar_inventario(
    ruta: str = RUTA_CSV,
    total: int = TOTAL_SERVIDORES
) -> None:
    """
    Genera el inventario CSV con servidores ficticios.

    CONCEPTO — Faker:
      Faker() crea un generador de datos falsos.
      fake.ipv4() genera una IP aleatoria como "192.168.1.45"
      fake.mac_address() genera una MAC como "aa:bb:cc:dd:ee:ff"
      fake.date_this_decade() genera una fecha de esta década

    CONCEPTO — csv.DictWriter:
      Escribe un CSV usando diccionarios.
      Cada fila es un diccionario donde las claves
      son los nombres de las columnas.

    CONCEPTO — random.choice():
      Elige un elemento aleatorio de una lista.
      random.choice(["a", "b", "c"]) devuelve "a", "b" o "c"

    CONCEPTO — random.randint(a, b):
      Genera un número entero aleatorio entre a y b.
    """

    # Inicializamos Faker en español
    fake = Faker("es_ES")

    # Columnas del CSV
    columnas: list[str] = [
        "id",
        "hostname",
        "ip",
        "mac",
        "sistema_operativo",
        "ram_gb",
        "cpu_cores",
        "departamento",
        "rol",
        "estado",
        "fecha_instalacion",
        "ultimo_backup"
    ]

    print(f"\n  Generando {total} servidores ficticios...")

    # Abrimos el fichero CSV para escritura
    # newline='' es necesario en Windows para evitar líneas dobles
    with open(ruta, "w", newline="", encoding="utf-8") as fichero:

        # DictWriter escribe filas como diccionarios
        writer = csv.DictWriter(fichero, fieldnames=columnas)

        # Escribe la cabecera (nombres de columnas)
        writer.writeheader()

        # Generamos cada servidor
        for i in range(1, total + 1):

            # Elegimos SO aleatorio
            so: str = random.choice(SISTEMAS_OPERATIVOS)

            # Generamos nombre de servidor según el SO
            if "Windows" in so:
                hostname: str = f"WIN-SRV-{i:04d}"
            else:
                hostname = f"linux-srv-{i:04d}"

            # Creamos la fila como diccionario
            fila: dict[str, str | int] = {
                "id":                  i,
                "hostname":            hostname,
                "ip":                  fake.ipv4(),
                "mac":                 fake.mac_address(),
                "sistema_operativo":   so,
                "ram_gb":              random.choice(RAM_OPCIONES),
                "cpu_cores":           random.choice([2, 4, 8, 16, 32]),
                "departamento":        random.choice(DEPARTAMENTOS),
                "rol":                 random.choice(ROLES),
                "estado":              random.choice(ESTADOS),
                "fecha_instalacion":   str(fake.date_this_decade()),
                "ultimo_backup":       str(fake.date_this_year())
            }

            writer.writerow(fila)

            # Mostramos progreso cada 100 servidores
            if i % 100 == 0:
                print(f"  [{i}/{total}] servidores generados...")

    print(f"\n  ✓ Inventario guardado en {ruta}")
    print(f"  ✓ {total} servidores generados correctamente")


# ─── PUNTO DE ARRANQUE ────────────────────────────────────────

if __name__ == "__main__":
    generar_inventario()