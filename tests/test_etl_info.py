"""
tests/test_etl_info.py
─────────────────────────────────────────────────────────────────────────────
Pruebas unitarias para las funciones de src/etl_info.py y src/charts.py.
No requieren conexión a MySQL.
"""

import sys
import pathlib
import pytest
import pandas as pd

# Agregar raíz del proyecto al path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.etl_info import (
    cargar_resumen,
    resumen_general,
    filas_por_archivo,
    reglas_limpieza,
    tablas_esperadas,
)


# ─── Tests de etl_info ───────────────────────────────────────────────────────

def test_cargar_resumen_devuelve_dict():
    """El JSON se carga correctamente como diccionario."""
    data = cargar_resumen()
    assert isinstance(data, dict)
    assert "resumen" in data
    assert "filas_por_archivo" in data


def test_resumen_general_claves():
    """El resumen general contiene todas las claves esperadas."""
    res = resumen_general()
    claves_esperadas = [
        "archivos", "filas_leidas", "otros_estados", "oaxaca",
        "rechazados_por_error", "identicos_eliminados", "finales",
        "coordenadas_en_nulo", "llaves_repetidas_precio_distinto",
        "precios_atipicos", "duracion",
    ]
    for clave in claves_esperadas:
        assert clave in res, f"Falta la clave: {clave}"


def test_resumen_valores_correctos():
    """Los valores numéricos del resumen son consistentes."""
    res = resumen_general()
    assert res["archivos"]     == 16
    assert res["filas_leidas"] == 9_388_457
    assert res["oaxaca"]       == 191_903
    assert res["finales"]      == 191_895
    # La diferencia oaxaca - finales debe ser ≥ duplicados eliminados
    assert res["oaxaca"] - res["finales"] >= res["identicos_eliminados"]


def test_filas_por_archivo_dataframe():
    """filas_por_archivo devuelve un DataFrame con las columnas correctas."""
    df = filas_por_archivo()
    assert isinstance(df, pd.DataFrame)
    assert "archivo" in df.columns
    assert "filas"   in df.columns
    assert len(df)   == 16


def test_filas_por_archivo_total():
    """La suma de filas por archivo coincide con el total leído."""
    df  = filas_por_archivo()
    res = resumen_general()
    assert df["filas"].sum() == res["filas_leidas"]


def test_reglas_limpieza_dataframe():
    """reglas_limpieza devuelve un DataFrame no vacío."""
    df = reglas_limpieza()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "regla"    in df.columns
    assert "cantidad" in df.columns


def test_tablas_esperadas_dataframe():
    """tablas_esperadas devuelve DataFrame con las tablas del DW y OLTP."""
    df = tablas_esperadas()
    assert isinstance(df, pd.DataFrame)
    assert "tabla"    in df.columns
    assert "esperado" in df.columns
    # Debe incluir fact_precio y agg_precio_mensual
    tablas = df["tabla"].tolist()
    assert any("fact_precio" in t for t in tablas)
    assert any("agg_precio_mensual" in t for t in tablas)


# ─── Tests de formateo de números ────────────────────────────────────────────

def test_formato_miles():
    """Verifica que el formato de miles funciona correctamente."""
    valor = 191_895
    formateado = f"{valor:,}"
    assert formateado == "191,895"


def test_formato_precio():
    """Verifica el formato de precio con dos decimales."""
    precio = 24.5
    formateado = f"${precio:,.2f}"
    assert formateado == "$24.50"


# ─── Tests de charts (sin Streamlit) ─────────────────────────────────────────

def test_embudo_etl_devuelve_figura():
    """La función embudo_etl devuelve un objeto Figure de Plotly."""
    import plotly.graph_objects as go
    from src.charts import embudo_etl
    fig = embudo_etl(9_388_457, 191_903, 191_895)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_barras_por_archivo_devuelve_figura():
    """La función barras_por_archivo devuelve un objeto Figure."""
    import plotly.graph_objects as go
    from src.charts import barras_por_archivo
    df = filas_por_archivo()
    fig = barras_por_archivo(df)
    assert isinstance(fig, go.Figure)


def test_barras_precio_cadena():
    """La función barras_precio_cadena acepta un DataFrame estándar."""
    import plotly.graph_objects as go
    from src.charts import barras_precio_cadena
    df = pd.DataFrame({
        "cadena_comercial": ["Walmart", "Chedraui", "Soriana"],
        "precio_promedio":  [23.50,     24.00,       22.80],
        "precio_minimo":    [20.00,     21.00,       19.50],
        "precio_maximo":    [27.00,     28.00,       26.00],
        "num_registros":    [100,       200,          150],
    })
    fig = barras_precio_cadena(df, "LECHE ENTERA")
    assert isinstance(fig, go.Figure)


def test_linea_serie_tiempo():
    """La función linea_serie_tiempo genera una figura con trazas."""
    import plotly.graph_objects as go
    from src.charts import linea_serie_tiempo
    df = pd.DataFrame({
        "mes":              [1, 2, 3, 1, 2, 3],
        "cadena_comercial": ["Walmart"]*3 + ["Chedraui"]*3,
        "precio_promedio":  [23.0, 23.5, 24.0, 22.0, 22.5, 23.0],
        "num_registros":    [100]*6,
    })
    fig = linea_serie_tiempo(df, "LECHE ENTERA")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # Una traza por cadena
