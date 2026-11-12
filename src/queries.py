"""
src/queries.py
─────────────────────────────────────────────────────────────────────────────
Todas las consultas SQL del dashboard conectadas directamente a MySQL.
Las agregaciones se realizan en la base de datos para no cargar DataFrames
masivos en memoria.
"""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.db import get_engine_dw, get_engine_oltp

# ─── Utilidad interna ────────────────────────────────────────────────────────

def _query_dw(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Ejecuta una consulta en el esquema DW y devuelve un DataFrame."""
    engine = get_engine_dw()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

def _query_oltp(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Ejecuta una consulta en el esquema OLTP y devuelve un DataFrame."""
    engine = get_engine_oltp()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

# ─── Conciliación ───────────────────────────────────────────────────────────

def contar_tabla(tabla: str, esquema: str) -> int | None:
    """Devuelve el conteo real de filas de una tabla en MySQL."""
    try:
        sql = f"SELECT COUNT(*) FROM `{esquema}`.`{tabla}`"
        engine = get_engine_dw() if "dw" in esquema else get_engine_oltp()
        with engine.connect() as conn:
            return conn.execute(text(sql)).scalar()
    except Exception:
        return None

# ─── Data Warehouse: conteos ─────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def conteo_tablas_dw() -> pd.DataFrame:
    """Conteo de filas de las tablas del DW directo desde MySQL."""
    sql = """
        SELECT 'fact_precio'         AS tabla, COUNT(*) AS filas FROM fact_precio
        UNION ALL
        SELECT 'dim_producto',         COUNT(*) FROM dim_producto
        UNION ALL
        SELECT 'dim_establecimiento',  COUNT(*) FROM dim_establecimiento
        UNION ALL
        SELECT 'dim_tiempo',           COUNT(*) FROM dim_tiempo
        UNION ALL
        SELECT 'agg_precio_mensual',   COUNT(*) FROM agg_precio_mensual
    """
    return _query_dw(sql)

# ─── Previews de tablas ──────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def preview_tabla_dw(tabla: str, limit: int = 500) -> pd.DataFrame:
    """Vista previa de una tabla del DW (limitada)."""
    tablas_validas = {
        "fact_precio", "dim_producto", "dim_establecimiento",
        "dim_tiempo", "agg_precio_mensual"
    }
    if tabla not in tablas_validas:
        return pd.DataFrame()
    return _query_dw(f"SELECT * FROM `{tabla}` LIMIT {limit}")

@st.cache_data(ttl=300, show_spinner=False)
def preview_tabla_oltp(tabla: str, limit: int = 200) -> pd.DataFrame:
    """Vista previa de una tabla del OLTP (limitada)."""
    tablas_validas = {
        "stg_qqp", "registro_precio", "producto",
        "presentacion_producto", "establecimiento"
    }
    if tabla not in tablas_validas:
        return pd.DataFrame()
    return _query_oltp(f"SELECT * FROM `{tabla}` LIMIT {limit}")

# ─── Comparativo de precios ──────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def lista_productos() -> list[str]:
    """Lista de productos únicos en el data mart de MySQL."""
    sql = "SELECT DISTINCT producto FROM agg_precio_mensual ORDER BY producto"
    df = _query_dw(sql)
    return df["producto"].tolist() if not df.empty else []

@st.cache_data(ttl=300, show_spinner=False)
def lista_categorias() -> list[str]:
    """Lista de categorías únicas en el data mart de MySQL."""
    sql = "SELECT DISTINCT categoria FROM agg_precio_mensual ORDER BY categoria"
    df = _query_dw(sql)
    return df["categoria"].tolist() if not df.empty else []

@st.cache_data(ttl=300, show_spinner=False)
def lista_cadenas() -> list[str]:
    """Lista de cadenas comerciales en MySQL."""
    sql = "SELECT DISTINCT cadena_comercial FROM agg_precio_mensual ORDER BY cadena_comercial"
    df = _query_dw(sql)
    return df["cadena_comercial"].tolist() if not df.empty else []

@st.cache_data(ttl=300, show_spinner=False)
def comparativo_por_cadena(producto: str) -> pd.DataFrame:
    """
    Precio promedio, mínimo y máximo por cadena comercial para un producto.
    Usa agg_precio_mensual (data mart en MySQL).
    """
    sql = """
        SELECT
            cadena_comercial,
            ROUND(AVG(precio_promedio), 2)  AS precio_promedio,
            ROUND(MIN(precio_minimo),   2)  AS precio_minimo,
            ROUND(MAX(precio_maximo),   2)  AS precio_maximo,
            SUM(num_registros)              AS num_registros
        FROM agg_precio_mensual
        WHERE producto = :producto
        GROUP BY cadena_comercial
        ORDER BY precio_promedio
    """
    return _query_dw(sql, {"producto": producto})

@st.cache_data(ttl=300, show_spinner=False)
def productos_por_categoria(categoria: str) -> list[str]:
    """Lista de productos de una categoría específica en MySQL."""
    sql = """
        SELECT DISTINCT producto
        FROM agg_precio_mensual
        WHERE categoria = :categoria
        ORDER BY producto
    """
    df = _query_dw(sql, {"categoria": categoria})
    return df["producto"].tolist() if not df.empty else []

# ─── Series de tiempo ────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def serie_tiempo_producto(producto: str, cadenas: list[str] | None = None) -> pd.DataFrame:
    """
    Evolución mensual del precio promedio para un producto en MySQL,
    opcionalmente filtrada por lista de cadenas.
    """
    if cadenas:
        placeholders = ", ".join([f":c{i}" for i in range(len(cadenas))])
        sql = f"""
            SELECT mes, cadena_comercial,
                   ROUND(AVG(precio_promedio), 2) AS precio_promedio,
                   SUM(num_registros)             AS num_registros
            FROM agg_precio_mensual
            WHERE producto = :producto
              AND cadena_comercial IN ({placeholders})
            GROUP BY mes, cadena_comercial
            ORDER BY mes, cadena_comercial
        """
        params = {"producto": producto}
        params.update({f"c{i}": c for i, c in enumerate(cadenas)})
    else:
        sql = """
            SELECT mes, cadena_comercial,
                   ROUND(AVG(precio_promedio), 2) AS precio_promedio,
                   SUM(num_registros)             AS num_registros
            FROM agg_precio_mensual
            WHERE producto = :producto
            GROUP BY mes, cadena_comercial
            ORDER BY mes, cadena_comercial
        """
        params = {"producto": producto}
    return _query_dw(sql, params)

# ─── Mapa de establecimientos ────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def establecimientos_mapa() -> pd.DataFrame:
    """
    Establecimientos con coordenadas válidas y número de registros en fact_precio
    directo desde MySQL.
    """
    sql = """
        SELECT
            e.sk_establecimiento,
            e.nombre_comercial,
            e.cadena_comercial,
            e.municipio,
            e.latitud,
            e.longitud,
            COUNT(f.id_registro) AS num_registros
        FROM dim_establecimiento e
        LEFT JOIN fact_precio f ON f.sk_establecimiento = e.sk_establecimiento
        WHERE e.latitud  IS NOT NULL
          AND e.longitud IS NOT NULL
          AND e.latitud  BETWEEN 15.6 AND 18.2
          AND e.longitud BETWEEN -98.6 AND -93.6
        GROUP BY
            e.sk_establecimiento, e.nombre_comercial, e.cadena_comercial,
            e.municipio, e.latitud, e.longitud
        ORDER BY num_registros DESC
    """
    return _query_dw(sql)

# ─── Calidad de datos ────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def calidad_nulos_dw() -> pd.DataFrame:
    """Cuenta nulos en columnas clave de las tablas del DW en MySQL."""
    sql = """
        SELECT 'dim_establecimiento' AS tabla,
               'latitud'            AS columna,
               SUM(latitud IS NULL) AS nulos,
               COUNT(*)             AS total
        FROM dim_establecimiento
        UNION ALL
        SELECT 'dim_establecimiento', 'longitud',
               SUM(longitud IS NULL), COUNT(*) FROM dim_establecimiento
        UNION ALL
        SELECT 'fact_precio', 'precio',
               SUM(precio IS NULL), COUNT(*) FROM fact_precio
        UNION ALL
        SELECT 'dim_producto', 'marca',
               SUM(marca IS NULL OR marca = ''), COUNT(*) FROM dim_producto
    """
    return _query_dw(sql)

@st.cache_data(ttl=300, show_spinner=False)
def coordenadas_fuera_oaxaca() -> int:
    """Cuenta establecimientos con coordenadas fuera del bounding box de Oaxaca en MySQL."""
    sql = """
        SELECT COUNT(*) AS total
        FROM dim_establecimiento
        WHERE latitud  IS NOT NULL
          AND longitud IS NOT NULL
          AND (latitud  NOT BETWEEN 15.6 AND 18.2
               OR longitud NOT BETWEEN -98.6 AND -93.6)
    """
    df = _query_dw(sql)
    return int(df["total"].iloc[0]) if not df.empty else 0
