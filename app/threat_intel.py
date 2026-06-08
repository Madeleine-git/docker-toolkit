#!/usr/bin/env python3
"""
threat_intel.py
===============
Módulo de inteligencia de amenazas.

Conecta con la API pública ipinfo.io para geolocalizar las IPs detectadas como atacantes en el log SSH.

Conceptos que practicamos:
  - requests.get()  → petición HTTP GET a una API
  - response.json() → convertir respuesta JSON a diccionario
  - try/except      → manejar errores de red
  - Combinar datos  → cruzar IPs del log con datos de la API
"""

import time
import requests


# ─── CONSTANTES ──────────────────────────────────────────────
# URL base de la API. Añadimos la IP al final de cada consulta.
# ipinfo.io es gratuita hasta 50.000 consultas al mes.
API_BASE_URL: str = "https://ipinfo.io"

# Tiempo de espera entre consultas para no saturar la API
ESPERA_ENTRE_CONSULTAS: float = 1.0  # segundos

# Tiempo máximo de espera por respuesta de la API
TIMEOUT_SEGUNDOS: int = 10


# ─── FUNCIÓN 1: CONSULTAR UNA IP ─────────────────────────────

def consultar_ip(ip: str) -> dict[str, str]:
    """
    Consulta la API de ipinfo.io para obtener información geográfica y de organización de una IP.

    Parámetros:
      ip (str) → la dirección IP a consultar

    Devuelve:
      dict con los campos: ip, pais, ciudad, org
      Si hay error, devuelve campos con valor 'Desconocido'

    CONCEPTO — requests.get():
      Hace una petición HTTP GET a la URL indicada.
      Es exactamente lo mismo que escribir la URL en el navegador, pero desde Python y de forma controlada.

    CONCEPTO — response.json():
      La API devuelve texto en formato JSON.
      .json() lo convierte automáticamente en un diccionario de Python que podemos usar normalmente.

    CONCEPTO — .get() en diccionarios:
      dict.get("clave", "valor_por_defecto")
      Si la clave no existe, devuelve el valor por defecto en lugar de lanzar un error. Más seguro que dict["clave"].
    """

    # Resultado por defecto si algo falla
    resultado: dict[str, str] = {
        "ip":     ip,
        "pais":   "Desconocido",
        "ciudad": "Desconocido",
        "org":    "Desconocido"
    }

    try:
        # Construimos la URL completa
        # Ejemplo: https://ipinfo.io/185.220.101.45/json
        url: str = f"{API_BASE_URL}/{ip}/json"

        # Hacemos la petición GET
        # timeout evita que el programa se quede esperando
        respuesta = requests.get(url, timeout=TIMEOUT_SEGUNDOS)

        # Comprobamos que la respuesta fue exitosa
        # status_code 200 = OK
        # raise_for_status() lanza error si fue 404, 500, etc.
        respuesta.raise_for_status()

        # Convertimos el JSON a diccionario de Python
        datos: dict[str, str] = respuesta.json()

        # Extraemos los campos que nos interesan
        # .get() devuelve "Desconocido" si el campo no existe
        resultado["pais"]   = datos.get("country", "Desconocido")
        resultado["ciudad"] = datos.get("city",    "Desconocido")
        resultado["org"]    = datos.get("org",     "Desconocido")

    except requests.exceptions.Timeout:
        print(f"  [!] Timeout consultando {ip} — sin respuesta en {TIMEOUT_SEGUNDOS}s")

    except requests.exceptions.ConnectionError:
        print(f"  [!] Error de conexión consultando {ip} — comprueba internet")

    except requests.exceptions.HTTPError as e:
        print(f"  [!] Error HTTP consultando {ip}: {e}")

    except Exception as e:
        print(f"  [!] Error inesperado consultando {ip}: {e}")

    return resultado


# ─── FUNCIÓN 2: CONSULTAR VARIAS IPs ─────────────────────────

def consultar_multiples_ips(
    conteo_ips: dict[str, int]
) -> list[dict[str, str]]:
    """
    Consulta la API para cada IP del diccionario de conteo y combina los datos de geolocalización con los intentos.

    Parámetros:
      conteo_ips → diccionario {ip: intentos} del log_parser

    Devuelve:
      Lista de diccionarios con ip, intentos, pais, ciudad, org

    CONCEPTO — Combinar datos de dos fuentes:
      El log_parser nos da {ip: intentos}.
      La API nos da {ip: pais, ciudad, org}.
      Esta función cruza ambas fuentes en una sola lista.
    """
    resultados: list[dict[str, str]] = []

    total: int = len(conteo_ips)
    print(f"\n  Consultando {total} IPs en ipinfo.io...")
    print(f"  (espera {ESPERA_ENTRE_CONSULTAS}s entre consultas)\n")

    for i, (ip, intentos) in enumerate(conteo_ips.items(), 1):
        print(f"  [{i}/{total}] Consultando {ip}...", end=" ", flush=True)

        # Consultamos la API
        datos: dict[str, str] = consultar_ip(ip)

        # Añadimos el número de intentos del log
        datos["intentos"] = str(intentos)

        resultados.append(datos)
        print(f"✓ {datos['pais']} — {datos['org'][:40]}")

        # Esperamos entre consultas para no saturar la API
        if i < total:
            time.sleep(ESPERA_ENTRE_CONSULTAS)

    return resultados


# ─── FUNCIÓN 3: MOSTRAR LA TABLA ─────────────────────────────

def mostrar_tabla_amenazas(
    resultados: list[dict[str, str]]
) -> None:
    """
    Muestra una tabla formateada con los resultados
    de la consulta a la API.

    CONCEPTO — Formateo de columnas:
      Usamos f-strings con especificadores de ancho para que las columnas queden perfectamente alineadas.
      {texto:<20} = alineado a la izquierda, 20 caracteres
      {texto:>8}  = alineado a la derecha, 8 caracteres
    """

    if not resultados:
        print("\n  [INFO] No hay resultados que mostrar.")
        return

    # Ordenamos por número de intentos de mayor a menor
    resultados_ordenados = sorted(
        resultados,
        key=lambda x: int(x["intentos"]),
        reverse=True
    )

    print("\n  " + "═" * 75)
    print("  TABLA DE INTELIGENCIA DE AMENAZAS")
    print("  " + "═" * 75)
    print(
        f"  {'IP':<18} {'Intent.':>7}  "
        f"{'País':<6} {'Ciudad':<15} {'Organización'}"
    )
    print("  " + "─" * 75)

    for r in resultados_ordenados:
        # Truncamos la organización si es muy larga
        org: str = r["org"][:30] if len(r["org"]) > 30 else r["org"]
        ciudad: str = r["ciudad"][:13] if len(r["ciudad"]) > 13 else r["ciudad"]

        print(
            f"  {r['ip']:<18} {r['intentos']:>7}  "
            f"  {r['pais']:<4} {ciudad:<15} {org}"
        )

    print("  " + "═" * 75)


# ─── FUNCIÓN 4: ANÁLISIS COMPLETO ────────────────────────────

def analizar_amenazas(conteo_ips: dict[str, int]) -> None:
    """
    Función principal del módulo.
    Combina el conteo de IPs del log_parser con la geolocalización de la API y muestra la tabla final.
    """
    if not conteo_ips:
        print("\n  [INFO] No hay IPs para analizar.")
        print("  [INFO] Ejecuta primero el analizador de logs SSH.")
        return

    # Consultamos la API para cada IP
    resultados: list[dict[str, str]] = consultar_multiples_ips(conteo_ips)

    # Mostramos la tabla final
    mostrar_tabla_amenazas(resultados)


# ─── MENÚ INTERACTIVO ────────────────────────────────────────

def menu_threat_intel() -> None:
    """
    Submenú del módulo de inteligencia de amenazas.
    Primero analiza el log SSH y luego consulta la API.
    """
    # Importamos log_parser aquí para evitar importación circular
    import log_parser

    while True:
        print("\n  ── Inteligencia de amenazas ────────────────")
        print("  a.  Analizar log + geolocalizar IPs")
        print("  b.  Geolocalizar una IP manualmente")
        print("  v.  Volver al menú principal")
        print("  ────────────────────────────────────────────")

        opcion: str = input("\n  Elige una opción [a/b/v]: ").strip().lower()

        if opcion == "a":
            # Paso 1: leer el log y obtener conteo de IPs
            print("\n  Paso 1: Leyendo auth.log...")
            conteo: dict[str, int] = log_parser.parsear_log()

            if not conteo:
                print("  [!] No se encontraron IPs en el log.")
                continue

            print(f"  ✓ {len(conteo)} IPs detectadas en el log.")

            # Paso 2: consultar la API para cada IP
            analizar_amenazas(conteo)

        elif opcion == "b":
            ip: str = input("\n  Introduce la IP a geolocalizar: ").strip()
            if ip:
                print(f"\n  Consultando {ip}...")
                datos: dict[str, str] = consultar_ip(ip)
                print(f"\n  IP:           {datos['ip']}")
                print(f"  País:         {datos['pais']}")
                print(f"  Ciudad:       {datos['ciudad']}")
                print(f"  Organización: {datos['org']}")

        elif opcion == "v":
            break

        else:
            print("  [!] Opción no reconocida.")