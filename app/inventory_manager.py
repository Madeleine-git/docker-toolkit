#!/usr/bin/env python3
"""
inventory_manager.py
====================
Carga y analiza el inventario CSV con pandas.

Operaciones:
  - Cargar el CSV en un DataFrame
  - Filtrar servidores Windows o con menos de 4GB RAM
  - Agrupar por departamento y contar servidores
"""

import pandas as pd


# ─── CONSTANTES ──────────────────────────────────────────────
RUTA_CSV: str = "data/inventory.csv"


# ─── FUNCIÓN 1: CARGAR EL INVENTARIO ─────────────────────────

def cargar_inventario(ruta: str = RUTA_CSV) -> pd.DataFrame:
    """
    Carga el CSV en un DataFrame de pandas.

    CONCEPTO — DataFrame:
      Es una tabla de datos con filas y columnas.
      Exactamente como una hoja de Excel pero en Python.
      Pandas puede cargar CSVs de millones de filas
      en segundos y hacer operaciones complejas.

    CONCEPTO — pd.read_csv():
      Lee un fichero CSV y lo convierte en DataFrame.
      Una sola línea reemplaza todo el código de
      leer un CSV manualmente con open() y csv.reader().
    """
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
        print(f"\n  ✓ Inventario cargado: {len(df)} servidores")
        print(f"  ✓ Columnas: {list(df.columns)}")
        return df

    except FileNotFoundError:
        print(f"\n  [!] No se encontró {ruta}")
        print("  [!] Ejecuta primero generate_inventory.py")
        return pd.DataFrame()


# ─── FUNCIÓN 2: FILTRAR SERVIDORES ───────────────────────────

def filtrar_servidores_vulnerables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra y muestra servidores Windows o con menos de 4GB RAM.

    CONCEPTO — Filtrado en pandas:
      df[condición] devuelve solo las filas que cumplen
      la condición. Es como el filtro de Excel pero
      en una línea de código.

    CONCEPTO — str.contains():
      Busca texto dentro de una columna de texto.
      df["so"].str.contains("Windows") devuelve True
      para cada fila que tenga "Windows" en esa columna.

    CONCEPTO — Operador |  (OR lógico):
      condicion_a | condicion_b
      Devuelve True si se cumple A o B o ambas.
    """

    if df.empty:
        print("  [!] DataFrame vacío.")
        return df

    # Condición 1: servidores con Windows Server
    es_windows = df["sistema_operativo"].str.contains(
        "Windows", case=False, na=False
    )

    # Condición 2: servidores con menos de 4GB de RAM
    poca_ram = df["ram_gb"] < 4

    # Combinamos con OR: Windows O poca RAM
    vulnerables = df[es_windows | poca_ram].copy()

    # Mostramos el resultado
    print(f"\n  {'═' * 60}")
    print("  SERVIDORES VULNERABLES O CON WINDOWS")
    print(f"  {'═' * 60}")
    print(f"  Total encontrados: {len(vulnerables)}")
    print(f"  {'─' * 60}")

    # Mostramos las columnas más relevantes
    columnas_mostrar: list[str] = [
        "hostname", "sistema_operativo", "ram_gb",
        "departamento", "estado"
    ]

    # Convertimos a string para mostrar bien en consola
    print(
        vulnerables[columnas_mostrar]
        .to_string(index=False, max_rows=20)
    )

    if len(vulnerables) > 20:
        print(f"\n  ... y {len(vulnerables) - 20} más.")

    print(f"  {'═' * 60}")

    return vulnerables


# ─── FUNCIÓN 3: AGRUPAR POR DEPARTAMENTO ─────────────────────

def agrupar_por_departamento(df: pd.DataFrame) -> None:
    """
    Agrupa los servidores por departamento y cuenta cuántos
    tiene cada área.

    CONCEPTO — groupby():
      Agrupa filas que tienen el mismo valor en una columna.
      Como la tabla dinámica de Excel.
      df.groupby("departamento") agrupa todas las filas
      que tienen el mismo departamento.

    CONCEPTO — .size():
      Cuenta cuántas filas hay en cada grupo.

    CONCEPTO — .sort_values():
      Ordena los resultados. ascending=False = mayor a menor.
    """

    if df.empty:
        print("  [!] DataFrame vacío.")
        return

    # Agrupamos y contamos
    conteo = (
        df.groupby("departamento")
        .size()
        .reset_index(name="total_servidores")
        .sort_values("total_servidores", ascending=False)
    )

    print(f"\n  {'═' * 40}")
    print("  SERVIDORES POR DEPARTAMENTO")
    print(f"  {'═' * 40}")
    print(f"  {'Departamento':<20} {'Servidores':>10}")
    print(f"  {'─' * 40}")

    for _, fila in conteo.iterrows():
        # Barra visual proporcional
        barra_len: int = int(fila["total_servidores"] / 10)
        barra: str = "█" * barra_len
        print(
            f"  {fila['departamento']:<20} "
            f"{int(fila['total_servidores']):>10}  {barra}"
        )

    print(f"  {'─' * 40}")
    print(f"  {'TOTAL':<20} {len(df):>10}")
    print(f"  {'═' * 40}")


# ─── FUNCIÓN 4: RESUMEN GENERAL ──────────────────────────────

def mostrar_resumen(df: pd.DataFrame) -> None:
    """
    Muestra estadísticas generales del inventario.
    """
    if df.empty:
        return

    # Conteo por sistema operativo
    conteo_so = df["sistema_operativo"].value_counts()

    # RAM promedio
    ram_promedio: float = df["ram_gb"].mean()
    ram_minima: int = int(df["ram_gb"].min())
    ram_maxima: int = int(df["ram_gb"].max())

    # Conteo por estado
    conteo_estado = df["estado"].value_counts()

    print(f"\n  {'═' * 50}")
    print("  RESUMEN GENERAL DEL INVENTARIO")
    print(f"  {'═' * 50}")
    print(f"  Total servidores:    {len(df)}")
    print(f"  RAM promedio:        {ram_promedio:.1f} GB")
    print(f"  RAM mínima:          {ram_minima} GB")
    print(f"  RAM máxima:          {ram_maxima} GB")

    print(f"\n  Sistemas operativos:")
    for so, cantidad in conteo_so.items():
        print(f"    {so:<35} {cantidad:>5}")

    print(f"\n  Estados:")
    for estado, cantidad in conteo_estado.items():
        print(f"    {estado:<20} {cantidad:>5}")

    print(f"  {'═' * 50}")


# ─── MENÚ INTERACTIVO ────────────────────────────────────────

def menu_inventory_manager() -> None:
    """
    Submenú del módulo de gestión de inventarios.
    """
    import generate_inventory

    while True:
        print("\n  ── Gestión de inventarios ──────────────────")
        print("  a.  Generar inventario CSV (1000 servidores)")
        print("  b.  Ver resumen general")
        print("  c.  Filtrar servidores vulnerables")
        print("  d.  Servidores por departamento")
        print("  v.  Volver al menú principal")
        print("  ────────────────────────────────────────────")

        opcion: str = input("\n  Elige una opción [a/b/c/d/v]: ").strip().lower()

        if opcion == "a":
            generate_inventory.generar_inventario()

        elif opcion in ["b", "c", "d"]:
            df = cargar_inventario()
            if df.empty:
                continue
            if opcion == "b":
                mostrar_resumen(df)
            elif opcion == "c":
                filtrar_servidores_vulnerables(df)
            elif opcion == "d":
                agrupar_por_departamento(df)

        elif opcion == "v":
            break

        else:
            print("  [!] Opción no reconocida.")