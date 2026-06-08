#!/usr/bin/env python3
"""
cli.py
======
Interfaz de línea de comandos profesional con Typer.

Mejora aplicada:
  04 - CLI con Typer en lugar de menú con input()

Uso:
  python3 cli.py --help
  python3 cli.py ping 8.8.8.8
  python3 cli.py disco /
  python3 cli.py logs analizar
  python3 cli.py logs ips
  python3 cli.py inventario generar
  python3 cli.py inventario vulnerables
  python3 cli.py inventario departamentos
  python3 cli.py informe generar
  python3 cli.py amenazas analizar
  python3 cli.py red auditar
"""

import typer
from typing import Optional
from logger import configurar_logger

# ─── LOGGER ──────────────────────────────────────────────────
logger = configurar_logger("cli")

# ─── APP PRINCIPAL ───────────────────────────────────────────
app = typer.Typer(
    name="sys-toolkit",
    help="Kit de herramientas para administradores de sistemas.",
    add_completion=False
)

# ─── SUBCOMANDOS ─────────────────────────────────────────────
# Cada grupo de comandos es una app separada
ping_app       = typer.Typer(help="Herramientas de red: ping y disco")
logs_app       = typer.Typer(help="Análisis de logs SSH")
inventario_app = typer.Typer(help="Gestión de inventario de servidores")
informe_app    = typer.Typer(help="Generación de informes Excel")
amenazas_app   = typer.Typer(help="Inteligencia de amenazas con API")
red_app        = typer.Typer(help="Modelos de red con POO")

app.add_typer(ping_app,       name="ping")
app.add_typer(logs_app,       name="logs")
app.add_typer(inventario_app, name="inventario")
app.add_typer(informe_app,    name="informe")
app.add_typer(amenazas_app,   name="amenazas")
app.add_typer(red_app,        name="red")


# ─── COMANDOS DE PING Y DISCO ────────────────────────────────

@ping_app.command("ip")
def cmd_ping(
    ip: str = typer.Argument(..., help="IP a comprobar. Ejemplo: 8.8.8.8")
) -> None:
    """Comprueba si una IP responde a ping."""
    from os_utils import check_ping
    typer.echo(f"Haciendo ping a {ip}...")
    if check_ping(ip):
        typer.secho(f"✓  {ip} está ACTIVA", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗  {ip} NO responde", fg=typer.colors.RED)


@ping_app.command("disco")
def cmd_disco(
    ruta: str = typer.Argument("/", help="Ruta a analizar. Ejemplo: /")
) -> None:
    """Comprueba el espacio libre en disco."""
    from os_utils import check_disk
    check_disk(ruta)


# ─── COMANDOS DE LOGS ────────────────────────────────────────

@logs_app.command("analizar")
def cmd_logs_analizar(
    fichero: str = typer.Option(
        "logs/auth.log",
        "--fichero", "-f",
        help="Ruta al fichero auth.log"
    )
) -> None:
    """Analiza auth.log y muestra reporte de IPs atacantes."""
    from log_parser import parsear_log, mostrar_reporte
    typer.echo(f"Analizando {fichero}...")
    conteo = parsear_log(fichero)
    mostrar_reporte(conteo)


@logs_app.command("ips")
def cmd_logs_ips(
    fichero: str = typer.Option(
        "logs/auth.log",
        "--fichero", "-f",
        help="Ruta al fichero auth.log"
    )
) -> None:
    """Muestra solo las IPs únicas detectadas."""
    from log_parser import parsear_log, obtener_ips_sospechosas
    conteo = parsear_log(fichero)
    ips = obtener_ips_sospechosas(conteo)
    typer.echo(f"\nIPs únicas que intentaron acceso: {len(ips)}")
    for ip in sorted(ips):
        typer.echo(f"  → {ip}")


# ─── COMANDOS DE INVENTARIO ──────────────────────────────────

@inventario_app.command("generar")
def cmd_inventario_generar(
    total: int = typer.Option(
        1000,
        "--total", "-n",
        help="Número de servidores a generar"
    )
) -> None:
    """Genera el inventario CSV con servidores ficticios."""
    from generate_inventory import generar_inventario
    generar_inventario(total=total)


@inventario_app.command("vulnerables")
def cmd_inventario_vulnerables() -> None:
    """Filtra y muestra servidores Windows o con RAM < 4GB."""
    from inventory_manager import cargar_inventario, filtrar_servidores_vulnerables
    df = cargar_inventario()
    if not df.empty:
        filtrar_servidores_vulnerables(df)


@inventario_app.command("departamentos")
def cmd_inventario_departamentos() -> None:
    """Agrupa servidores por departamento."""
    from inventory_manager import cargar_inventario, agrupar_por_departamento
    df = cargar_inventario()
    if not df.empty:
        agrupar_por_departamento(df)


@inventario_app.command("resumen")
def cmd_inventario_resumen() -> None:
    """Muestra resumen estadístico del inventario."""
    from inventory_manager import cargar_inventario, mostrar_resumen
    df = cargar_inventario()
    if not df.empty:
        mostrar_resumen(df)


# ─── COMANDOS DE INFORME ─────────────────────────────────────

@informe_app.command("generar")
def cmd_informe_generar() -> None:
    """Genera el informe Excel ejecutivo."""
    from report_generator import generar_informe_excel
    generar_informe_excel()


# ─── COMANDOS DE AMENAZAS ────────────────────────────────────

@amenazas_app.command("analizar")
def cmd_amenazas_analizar() -> None:
    """Analiza log SSH y geolocaliza IPs atacantes."""
    from log_parser import parsear_log
    from threat_intel import analizar_amenazas
    conteo = parsear_log()
    analizar_amenazas(conteo)


@amenazas_app.command("ip")
def cmd_amenazas_ip(
    ip: str = typer.Argument(..., help="IP a geolocalizar")
) -> None:
    """Geolocaliza una IP específica."""
    from threat_intel import consultar_ip
    typer.echo(f"Consultando {ip}...")
    datos = consultar_ip(ip)
    typer.echo(f"\n  IP:           {datos['ip']}")
    typer.echo(f"  País:         {datos['pais']}")
    typer.echo(f"  Ciudad:       {datos['ciudad']}")
    typer.echo(f"  Organización: {datos['org']}")


# ─── COMANDOS DE RED ─────────────────────────────────────────

@red_app.command("auditar")
def cmd_red_auditar() -> None:
    """Audita todos los dispositivos de red."""
    from network_models import Router, Server, NetworkDevice
    dispositivos: list[NetworkDevice] = [
        Router("router-core-01", "192.168.1.1", "AA:BB:CC:DD:EE:01",
               interfaces=8, gateway="10.0.0.1"),
        Server("server-web-01", "192.168.1.10", "AA:BB:CC:DD:EE:02",
               sistema_operativo="Ubuntu 22.04", ram_gb=16,
               servicios=["nginx", "ssh", "postgresql"]),
        Server("server-db-01", "192.168.1.11", "AA:BB:CC:DD:EE:03",
               sistema_operativo="Windows Server 2019", ram_gb=32,
               servicios=["sqlserver", "rdp", "iis"]),
    ]
    for d in dispositivos:
        d.audit_device()


# ─── PUNTO DE ARRANQUE ───────────────────────────────────────

if __name__ == "__main__":
    app()