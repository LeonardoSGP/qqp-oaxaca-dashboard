"""
pages/5_Mapa.py
─────────────────────────────────────────────────────────────────────────────
Página 5: Mapa de establecimientos en Oaxaca con diseño Glassmorphism.
Muestra las tiendas con coordenadas válidas usando Plotly Scattermap/Scattermapbox.
El tamaño y color de cada punto indica el número de registros en fact_precio.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from src.queries import establecimientos_mapa
from src.charts import mapa_establecimientos
from src.theme import apply_glassmorphism

apply_glassmorphism()

st.title("Mapa de establecimientos — Oaxaca")
st.markdown(
    "Establecimientos registrados en el programa *Quién es Quién en los Precios* "
    "con coordenadas válidas dentro del estado de Oaxaca."
)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Cargar datos ─────────────────────────────────────────────────────────────
with st.spinner("Cargando establecimientos desde MySQL…"):
    df = establecimientos_mapa()

if df.empty:
    st.warning("No se encontraron establecimientos con coordenadas válidas.")
    st.stop()

# ─── KPIs con altura de referencia unificada ─────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
for col, valor, label, sub in [
    (k1, f"{len(df)}",                          "Establecimientos con coords", "Cobertura verificada"),
    (k2, f"{df['cadena_comercial'].nunique()}", "Cadenas representadas",       "Supermercados y comercios"),
    (k3, f"{df['municipio'].nunique()}",        "Municipios",                  "Estado de Oaxaca"),
    (k4, f"{int(df['num_registros'].sum()):,}", "Registros totales",           "Observaciones en fact_precio"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card glass-card"><p class="kpi-valor">{valor}</p>'
            f'<p class="kpi-label">{label}</p><p class="kpi-sub">{sub}</p></div>',
            unsafe_allow_html=True,
        )

st.info(
    "Nota de georreferenciación: Se agregaron las coordenadas faltantes para el establecimiento "
    "«Farmacia Hospital Reforma» (17.069029, -96.721632 vía Google Maps), alcanzando una "
    "cobertura geográfica del 100% (51 de 51 tiendas y 191,895 registros totales en el mapa)."
)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Filtros superiores de estilo y cadena ───────────────────────────────────
f_col1, f_col2 = st.columns([1, 2])

with f_col1:
    estilos_mapa = {
        "OpenStreetMap (Calles detallado)": "open-street-map",
        "Carto Positron (Claro)": "carto-positron",
        "Carto Darkmatter (Oscuro)": "carto-darkmatter",
    }
    if not os.getenv("MAPBOX_TOKEN", "").strip():
        load_dotenv(override=True)
    if os.getenv("MAPBOX_TOKEN", "").strip():
        estilos_mapa.update({
            "Mapbox Streets": "streets",
            "Mapbox Dark": "dark",
            "Mapbox Satellite Streets": "satellite-streets",
        })
    estilo_label = st.selectbox("Estilo de mapa", options=list(estilos_mapa.keys()), index=0)
    estilo_sel = estilos_mapa[estilo_label]

with f_col2:
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
fig = mapa_establecimientos(df_map, estilo=estilo_sel)
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    },
)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Tabla ─────────────────────────────────────────────────────────────────────
st.markdown("### Listado de establecimientos")
df_tabla = df_map[["nombre_comercial", "cadena_comercial", "municipio", "latitud", "longitud", "num_registros"]].copy()
df_tabla["num_registros"] = df_tabla["num_registros"].apply(lambda v: f"{int(v):,}")
df_tabla.columns = ["Nombre comercial", "Cadena", "Municipio", "Latitud", "Longitud", "Registros"]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)
