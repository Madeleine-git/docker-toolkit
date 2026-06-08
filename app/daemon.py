#!/usr/bin/env python3
"""
daemon.py
=========
Ejecuta el toolkit automáticamente cada hora como demonio.
Lee el auth.log, analiza IPs y genera informe Excel.
"""

import schedule
import time
from datetime import datetime
import log_parser
import report_generator


def ejecutar_ciclo_completo() -> None:
    """
    Ciclo completo automático:
    1. Analiza el log SSH
    2. Genera informe Excel
    """
    ahora: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n[{ahora}] Iniciando ciclo automático...")

    # Paso 1: analizar logs
    print(f"[{ahora}] Analizando auth.log...")
    conteo = log_parser.parsear_log()
    print(f"[{ahora}] IPs detectadas: {len(conteo)}")

    # Paso 2: generar informe Excel
    print(f"[{ahora}] Generando informe Excel...")
    report_generator.generar_informe_excel()

    print(f"[{ahora}] Ciclo completado.")


def main() -> None:
    """
    Inicia el demonio que se ejecuta cada hora.
    """
    print("=" * 50)
    print("  SysAdmin Toolkit — Modo Demonio")
    print("  Ejecución automática cada hora")
    print("  Pulsa Ctrl+C para detener")
    print("=" * 50)

    # Programamos la tarea cada hora
    schedule.every().hour.do(ejecutar_ciclo_completo)

    # Ejecutamos una vez al arrancar
    ejecutar_ciclo_completo()

    # Bucle infinito que mantiene el demonio vivo
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # comprueba cada minuto
    except KeyboardInterrupt:
        print("\n  Demonio detenido.")


if __name__ == "__main__":
    main()