"""
pages/5_🗺️_Mapa.py
─────────────────────────────────────────────────────────────────────────────
Página 5: Mapa de establecimientos en Oaxaca.
Muestra las tiendas con coordenadas válidas usando Plotly Scattermapbox
con estilo carto-darkmatter (sin token requerido).
El tamaño y color de cada punto indica el número de registros en fact_precio.
"""

import streamlit as st
import pandas as pd
from src.queries import establecimientos_mapa
from src.charts import mapa_establecimientos
from src.db import is_connected

st.markdown("""
<style>
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Mapa de establecimientos — Oaxaca")
st.markdown(
    "Establecimientos registrados en el programa *Quién es Quién en los Precios* "
    "con coordenadas válidas dentro del estado de Oaxaca."
)

if not is_connected():
    st.info("ℹ️ Modo demo activo. Se muestran datos de muestra.", icon="ℹ️")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Cargar datos ─────────────────────────────────────────────────────────────
with st.spinner("Cargando establecimientos…"):
    df = establecimientos_mapa()

if df.empty:
    st.warning("No se encontraron establecimientos con coordenadas válidas.")
    st.stop()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
for col, valor, label in [
    (k1, f"{len(df)}",                              "Establecimientos con coords"),
    (k2, f"{df['cadena_comercial'].nunique()}",      "Cadenas representadas"),
    (k3, f"{df['municipio'].nunique()}",             "Municipios"),
    (k4, f"{int(df['num_registros'].sum()):,}",     "Registros totales"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-valor">{valor}</p>
            <p class="kpi-label">{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Filtro por cadena (sidebar) ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtros")
    cadenas_disp = sorted(df["cadena_comercial"].dropna().unique().tolist())
    cadenas_sel  = st.multiselect(
        "Filtrar por cadena",
        options=cadenas_disp,
        default=cadenas_disp,
    )

if cadenas_sel:
    df_map = df[df["cadena_comercial"].isin(cadenas_sel)]
else:
    df_map = df

st.caption(f"Mostrando {len(df_map)} establecimientos")

# ─── Mapa ──────────────────────────────────────────────────────────────────────
fig = mapa_establecimientos(df_map)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Tabla ─────────────────────────────────────────────────────────────────────
st.markdown("### 📋 Listado de establecimientos")
df_tabla = df_map[["nombre_comercial","cadena_comercial","municipio","latitud","longitud","num_registros"]].copy()
df_tabla["num_registros"] = df_tabla["num_registros"].apply(lambda v: f"{int(v):,}")
df_tabla.columns = ["Nombre comercial","Cadena","Municipio","Latitud","Longitud","Registros"]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)
