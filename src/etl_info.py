"""
src/etl_info.py
─────────────────────────────────────────────────────────────────────────────
Carga y expone los datos del proceso ETL desde data/etl_resumen.json.
"""

import json
import pathlib
import pandas as pd

_RUTA = pathlib.Path(__file__).parent.parent / "data" / "etl_resumen.json"


def cargar_resumen() -> dict:
    """Devuelve el JSON completo del resumen ETL."""
    with open(_RUTA, encoding="utf-8") as f:
        return json.load(f)


def resumen_general() -> dict:
    """Devuelve solo la sección 'resumen' del JSON."""
    return cargar_resumen()["resumen"]


def filas_por_archivo() -> pd.DataFrame:
    """Devuelve un DataFrame con columnas [archivo, filas]."""
    datos = cargar_resumen()["filas_por_archivo"]
    return pd.DataFrame(datos)


def reglas_limpieza() -> pd.DataFrame:
    """Devuelve un DataFrame con columnas [regla, cantidad]."""
    datos = cargar_resumen()["reglas_limpieza"]
    return pd.DataFrame(datos)


def tablas_esperadas() -> pd.DataFrame:
    """Devuelve un DataFrame con [tabla, esquema, esperado]."""
    datos = cargar_resumen()["tablas_esperadas"]
    return pd.DataFrame(datos)
