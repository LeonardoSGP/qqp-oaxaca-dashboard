"""
pages/2_Data_Warehouse.py
─────────────────────────────────────────────────────────────────────────────
Página 2: Data Warehouse y Data Mart.
Muestra el diagrama del modelo en estrella, conteo de filas por tabla,
vistas previas paginadas de cada tabla y descripción del data mart.
"""

import streamlit as st
from src.queries import conteo_tablas_dw, preview_tabla_dw, preview_tabla_oltp
from src.charts import barras_conteo_tablas

st.markdown("""
<style>
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
.kpi-sub   { font-size:0.75rem; color:#64748B; }
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Data Warehouse y Data Mart")
st.markdown("Arquitectura del modelo de datos, conteos de filas y vistas previas de tablas.")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Diagrama del modelo en estrella ─────────────────────────────────────────
st.markdown("### Modelo en estrella — esquema `qqp_dw`")
st.markdown("""
```mermaid
erDiagram
    fact_precio {
        int id_registro PK
        int sk_producto FK
        int sk_establecimiento FK
        date id_tiempo FK
        decimal precio
    }
    dim_producto {
        int sk_producto PK
        int id_presentacion_origen
        string producto
        string presentacion
        string marca
        string categoria
        string catalogo
    }
    dim_establecimiento {
        int sk_establecimiento PK
        int id_establecimiento_origen
        string nombre_comercial
        string cadena_comercial
        string giro
        string direccion
        string municipio
        string estado
        float latitud
        float longitud
    }
    dim_tiempo {
        date id_tiempo PK
        date fecha
        int anio
        int trimestre
        int mes
        string nombre_mes
        int dia
        int semana_iso
        string dia_semana
        bool es_dia_habil
    }
    fact_precio }o--|| dim_producto : "sk_producto"
    fact_precio }o--|| dim_establecimiento : "sk_establecimiento"
    fact_precio }o--|| dim_tiempo : "id_tiempo"
```
""")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Conteo de filas por tabla ────────────────────────────────────────────────
st.markdown("### Conteo de filas por tabla")

df_cont = conteo_tablas_dw()

if not df_cont.empty:
    fig = barras_conteo_tablas(df_cont)
    st.plotly_chart(fig, use_container_width=True)

    # KPIs rápidos
    k1, k2, k3, k4, k5 = st.columns(5)
    for col, row in zip([k1, k2, k3, k4, k5], df_cont.itertuples()):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-valor">{row.filas:,}</p>
                <p class="kpi-label">{row.tabla}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No se pudieron obtener los conteos.")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Data Mart ───────────────────────────────────────────────────────────────
st.markdown("### Data Mart — `agg_precio_mensual`")
st.markdown("""
La tabla `agg_precio_mensual` es el **data mart** del proyecto. Contiene
agregaciones pre-calculadas a nivel mensual, pensadas para alimentar
directamente los reportes y gráficas sin procesar las ~191,895 filas de
`fact_precio` en cada consulta.

| Columna | Descripción |
|---|---|
| `mes` | Número de mes (1–8) |
| `producto` | Nombre del producto |
| `presentacion` | Presentación del producto |
| `marca` | Marca del producto |
| `categoria` | Categoría Profeco |
| `cadena_comercial` | Nombre de la cadena de supermercado |
| `estado` | Estado (siempre Oaxaca en este dataset) |
| `precio_promedio` | Precio promedio del mes |
| `precio_minimo` | Precio mínimo registrado |
| `precio_maximo` | Precio máximo registrado |
| `num_registros` | Número de observaciones |

> **73,863 filas** pre-agregadas que reemplazan millones de operaciones en tiempo de consulta.
""")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Vistas previas paginadas ─────────────────────────────────────────────────
st.markdown("### Vista previa de tablas")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "fact_precio", "dim_producto", "dim_establecimiento", "dim_tiempo", "agg_precio_mensual"
])

TABLAS = [
    ("fact_precio",        tab1),
    ("dim_producto",       tab2),
    ("dim_establecimiento",tab3),
    ("dim_tiempo",         tab4),
    ("agg_precio_mensual", tab5),
]

for nombre, tab in TABLAS:
    with tab:
        with st.spinner(f"Cargando {nombre}…"):
            df = preview_tabla_dw(nombre, limit=200)
        if df.empty:
            st.warning(f"Sin datos disponibles para {nombre}.")
        else:
            st.caption(f"Mostrando hasta 200 filas de `{nombre}`")
            st.dataframe(df, use_container_width=True, height=400)
