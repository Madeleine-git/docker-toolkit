#!/usr/bin/env python3
"""
logger.py
=========
Configuración centralizada del sistema de logging.

Todos los módulos importan el logger desde aquí
para tener un formato consistente en todo el proyecto.

Niveles de log:
  DEBUG    → detalles internos para depuración
  INFO     → operación normal
  WARNING  → algo inesperado pero no crítico
  ERROR    → algo falló, el programa puede continuar
  CRITICAL → fallo grave
"""

import logging
import os
from datetime import datetime


# ─── CONSTANTES ──────────────────────────────────────────────
LOG_DIR: str  = "logs"
LOG_FILE: str = os.path.join(LOG_DIR, "toolkit.log")
LOG_LEVEL: int = logging.INFO


def configurar_logger(nombre: str) -> logging.Logger:
    """
    Crea y configura un logger con el nombre del módulo.

    Parámetros:
      nombre → nombre del módulo (ej: "log_parser", "os_utils")

    Devuelve:
      Logger configurado con dos destinos:
        - Consola (pantalla) → solo WARNING y superiores
        - Fichero toolkit.log → INFO y superiores

    CONCEPTO — Logger con nombre:
      Cada módulo tiene su propio logger con su nombre.
      Así en el fichero de log sabes exactamente qué módulo
      generó cada mensaje:
      2026-05-29 10:33:12 - log_parser - INFO - Analizando logs...
      2026-05-29 10:33:12 - os_utils   - WARNING - Disco bajo 20%

    CONCEPTO — Handlers:
      Un logger puede tener varios "destinos" (handlers).
      StreamHandler → escribe en pantalla
      FileHandler   → escribe en fichero
      Cada handler puede tener su propio nivel y formato.
    """

    # Creamos la carpeta de logs si no existe
    os.makedirs(LOG_DIR, exist_ok=True)

    # Obtenemos el logger con el nombre del módulo
    logger = logging.getLogger(nombre)
    logger.setLevel(LOG_LEVEL)

    # Evitamos añadir handlers duplicados si el logger
    # ya fue configurado anteriormente
    if logger.handlers:
        return logger

    # ── FORMATO DE LOS MENSAJES ───────────────────────────
    # %(asctime)s    → fecha y hora
    # %(name)s       → nombre del módulo
    # %(levelname)s  → nivel (INFO, WARNING, ERROR...)
    # %(message)s    → el mensaje en sí
    formato = logging.Formatter(
        fmt="%(asctime)s - %(name)-15s - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── HANDLER 1: CONSOLA ────────────────────────────────
    # Solo muestra WARNING, ERROR y CRITICAL en pantalla
    # Para no saturar la salida con mensajes INFO en producción
    consola = logging.StreamHandler()
    consola.setLevel(logging.WARNING)
    consola.setFormatter(formato)

    # ── HANDLER 2: FICHERO ────────────────────────────────
    # Guarda TODO (INFO y superior) en logs/toolkit.log
    # Así tienes historial completo para auditoría
    fichero_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fichero_handler.setLevel(logging.INFO)
    fichero_handler.setFormatter(formato)

    logger.addHandler(consola)
    logger.addHandler(fichero_handler)

    return logger