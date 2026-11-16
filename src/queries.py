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

@st.cache_data(ttl=600, show_spinner=False)
def contar_tabla(tabla: str, esquema: str) -> int | None:
    """Devuelve el conteo real de filas de una tabla en MySQL."""
    try:
        sql = f"SELECT COUNT(*) FROM `{esquema}`.`{tabla}`"
        engine = get_engine_dw() if "dw" in esquema else get_engine_oltp()
        with engine.connect() as conn:
            return conn.execute(text(sql)).scalar()
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def conciliacion_tablas() -> pd.DataFrame:
    """Conciliación en lote cacheada para evitar bloquear el cambio de páginas."""
    from src.etl_info import tablas_esperadas

    df_esp = tablas_esperadas()
    conteos_reales: dict[str, int] = {}
    err_str = "N/A"
    try:
        df_dw = _query_dw("""
            SELECT 'qqp_dw.fact_precio' AS tabla, COUNT(*) AS filas FROM fact_precio
            UNION ALL SELECT 'qqp_dw.dim_tiempo', COUNT(*) FROM dim_tiempo
            UNION ALL SELECT 'qqp_dw.dim_producto', COUNT(*) FROM dim_producto
            UNION ALL SELECT 'qqp_dw.dim_establecimiento', COUNT(*) FROM dim_establecimiento
            UNION ALL SELECT 'qqp_dw.agg_precio_mensual', COUNT(*) FROM agg_precio_mensual
        """)
        for r in df_dw.itertuples():
            conteos_reales[r.tabla] = int(r.filas)

        df_oltp = _query_oltp("""
            SELECT 'qqp_oltp.stg_qqp' AS tabla, COUNT(*) AS filas FROM stg_qqp
            UNION ALL SELECT 'qqp_oltp.registro_precio', COUNT(*) FROM registro_precio
            UNION ALL SELECT 'qqp_oltp.producto', COUNT(*) FROM producto
            UNION ALL SELECT 'qqp_oltp.presentacion_producto', COUNT(*) FROM presentacion_producto
        """)
        for r in df_oltp.itertuples():
            conteos_reales[r.tabla] = int(r.filas)
        if "qqp_oltp.registro_precio" in conteos_reales:
            conteos_reales["qqp_oltp.v_stg_limpio"] = conteos_reales["qqp_oltp.registro_precio"]
    except Exception as e:
        err_str = str(e)[:50]

    filas_conc = []
    for _, row in df_esp.iterrows():
        tabla_full = row["tabla"]
        esperado   = int(row["esperado"])
        real       = conteos_reales.get(tabla_full)
        if real is not None:
            diff     = real - esperado
            estado   = "OK" if diff == 0 else ("DIFERENCIA" if abs(diff) < 10 else "ERROR")
            diff_str = f"+{diff:,}" if diff > 0 else f"{diff:,}"
        else:
            estado   = "ERROR"
            diff_str = err_str
        filas_conc.append({
            "Estado": estado,
            "Tabla": tabla_full,
            "Esperado": f"{esperado:,}",
            "Real": f"{real:,}" if real is not None else "Error",
            "Diferencia": diff_str,
        })
    return pd.DataFrame(filas_conc)

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

# ---------------------------------------------------------------------------
# KPIs de la canasta básica – consultas específicas
# ---------------------------------------------------------------------------

from src.config import CANASTA_PACIC, CANASTA_PRODUCTOS

# Helper – ejecuta consulta en DW
def _query_dw(sql: str, params: tuple | None = None) -> pd.DataFrame:
    engine = get_engine_dw()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

# 1. Precio promedio por producto
@st.cache_data(ttl=600, show_spinner=False)
def precio_promedio_por_producto() -> pd.DataFrame:
    sql = f"""
        SELECT
            ap.producto,
            ROUND(AVG(ap.precio_promedio), 2) AS precio_promedio,
            SUM(ap.num_registros)               AS num_registros,
            COUNT(DISTINCT ap.cadena_comercial) AS cadenas_cubiertas,
            COUNT(DISTINCT ap.establecimiento_id) AS establecimientos_cubiertos
        FROM agg_precio_mensual ap
        WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
          AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
        GROUP BY ap.producto
        ORDER BY precio_promedio DESC;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)

# 2. Precio máximo por producto
@st.cache_data(ttl=600, show_spinner=False)
def precio_maximo_por_producto() -> pd.DataFrame:
    sql = f"""
        SELECT
            ap.producto,
            ROUND(MAX(ap.precio_maximo), 2) AS precio_maximo,
            SUM(ap.num_registros)           AS num_registros,
            COUNT(DISTINCT ap.cadena_comercial) AS cadenas_cubiertas,
            COUNT(DISTINCT ap.establecimiento_id) AS establecimientos_cubiertos
        FROM agg_precio_mensual ap
        WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
          AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
        GROUP BY ap.producto
        ORDER BY precio_maximo DESC;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)

# 3. Precio mínimo por producto
@st.cache_data(ttl=600, show_spinner=False)
def precio_minimo_por_producto() -> pd.DataFrame:
    sql = f"""
        SELECT
            ap.producto,
            ROUND(MIN(ap.precio_minimo), 2) AS precio_minimo,
            SUM(ap.num_registros)           AS num_registros,
            COUNT(DISTINCT ap.cadena_comercial) AS cadenas_cubiertas,
            COUNT(DISTINCT ap.establecimiento_id) AS establecimientos_cubiertos
        FROM agg_precio_mensual ap
        WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
          AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
        GROUP BY ap.producto
        ORDER BY precio_minimo ASC;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)

# 4. Variación mensual del precio promedio (%)
@st.cache_data(ttl=600, show_spinner=False)
def variacion_mensual_promedio() -> pd.DataFrame:
    sql = f"""
        WITH base AS (
            SELECT
                ap.producto,
                CONCAT(ap.ano, '-', LPAD(ap.mes,2,'0')) AS periodo,
                ROUND(AVG(ap.precio_promedio),2) AS precio_prom
            FROM agg_precio_mensual ap
            WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
              AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
            GROUP BY ap.producto, ap.ano, ap.mes
        ),
        lagged AS (
            SELECT
                b.producto,
                b.periodo,
                b.precio_prom,
                LAG(b.precio_prom) OVER (PARTITION BY b.producto ORDER BY b.periodo) AS precio_anterior
            FROM base b
        )
        SELECT
            producto,
            periodo,
            CASE WHEN precio_anterior IS NULL THEN NULL
                 ELSE ROUND(100.0 * (precio_prom - precio_anterior) / precio_anterior,2)
            END AS variacion_pct
        FROM lagged
        ORDER BY producto, periodo;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)

# 5. Variación acumulada (primer mes vs último mes)
@st.cache_data(ttl=600, show_spinner=False)
def variacion_acumulada() -> pd.DataFrame:
    sql = f"""
        WITH primero AS (
            SELECT producto, AVG(precio_promedio) AS precio_inicio
            FROM agg_precio_mensual
            WHERE producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
              AND ano = 2026 AND mes = 1
            GROUP BY producto
        ),
        ultimo AS (
            SELECT producto, AVG(precio_promedio) AS precio_fin
            FROM agg_precio_mensual
            WHERE producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
              AND ano = 2026 AND mes = 8
            GROUP BY producto
        )
        SELECT
            p.producto,
            ROUND(p.precio_inicio,2) AS precio_inicio,
            ROUND(u.precio_fin,2)    AS precio_fin,
            ROUND(u.precio_fin - p.precio_inicio,2) AS delta_valor,
            ROUND(100.0 * (u.precio_fin - p.precio_inicio) / p.precio_inicio,2) AS delta_pct
        FROM primero p
        JOIN ultimo u USING (producto)
        ORDER BY delta_pct DESC;
    """
    params = tuple(CANASTA_PRODUCTOS * 2)
    return _query_dw(sql, params)

# 6. Top 10 productos más caros (por precio promedio)
@st.cache_data(ttl=600, show_spinner=False)
def top_productos_mas_caros() -> pd.DataFrame:
    df = precio_promedio_por_producto()
    return df.nlargest(10, 'precio_promedio')

# 7. Top 5 productos con mayor alza (variación acumulada)
@st.cache_data(ttl=600, show_spinner=False)
def top_productos_mayor_alza() -> pd.DataFrame:
    df = variacion_acumulada()
    return df.nlargest(5, 'delta_pct')

# 8. Top 5 productos más estables (menor variación absoluta)
@st.cache_data(ttl=600, show_spinner=False)
def top_productos_mas_estables() -> pd.DataFrame:
    df = variacion_acumulada().copy()
    df['abs_delta'] = df['delta_pct'].abs()
    return df.nsmallest(5, 'abs_delta')

# 9. Costo de la canasta por cadena (cobertura >= 20 productos)
@st.cache_data(ttl=600, show_spinner=False)
def costo_canasta_por_cadena() -> pd.DataFrame:
    sql = f"""
        SELECT
            ap.cadena_comercial,
            SUM(ap.precio_promedio) AS costo_promedio,
            COUNT(DISTINCT ap.producto) AS productos_cubiertos,
            SUM(ap.num_registros)      AS total_registros
        FROM agg_precio_mensual ap
        WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
          AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
        GROUP BY ap.cadena_comercial
        HAVING productos_cubiertos >= 20
        ORDER BY costo_promedio DESC;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)

# 10. Diferencia de precio entre cadenas por producto
@st.cache_data(ttl=600, show_spinner=False)
def diferencia_precio_entre_cadenas() -> pd.DataFrame:
    sql = f"""
        WITH precios AS (
            SELECT
                ap.producto,
                ap.cadena_comercial,
                ROUND(AVG(ap.precio_promedio),2) AS precio_promedio
            FROM agg_precio_mensual ap
            WHERE ap.producto COLLATE utf8mb4_0900_as_ci IN ({', '.join(['%s'] * len(CANASTA_PRODUCTOS))})
              AND ap.ano = 2026 AND ap.mes BETWEEN 1 AND 8
            GROUP BY ap.producto, ap.cadena_comercial
        ),
        rangos AS (
            SELECT
                p.producto,
                MAX(p.precio_promedio) AS max_precio,
                MIN(p.precio_promedio) AS min_precio,
                (MAX(p.precio_promedio) - MIN(p.precio_promedio)) / NULLIF(MIN(p.precio_promedio),0) * 100 AS variacion_pct,
                MAX(p.cadena_comercial) FILTER (WHERE p.precio_promedio = MAX(p.precio_promedio)) AS cadena_max,
                MIN(p.cadena_comercial) FILTER (WHERE p.precio_promedio = MIN(p.precio_promedio)) AS cadena_min
            FROM precios p
            GROUP BY p.producto
        )
        SELECT
            producto,
            cadena_max AS cadena_mas_cara,
            max_precio,
            cadena_min AS cadena_mas_barata,
            min_precio,
            ROUND(variacion_pct,2) AS variacion_pct
        FROM rangos
        ORDER BY variacion_pct DESC;
    """
    params = tuple(CANASTA_PRODUCTOS)
    return _query_dw(sql, params)
