"""
pages/3_💲_Comparativo_de_Precios.py
─────────────────────────────────────────────────────────────────────────────
Página 3: Comparativo de precios por cadena comercial.
Filtros en la barra lateral (categoría, producto); gráfica de barras de
precio promedio y tabla con mínimo, máximo y número de registros.
"""

import streamlit as st
import pandas as pd
from src.queries import lista_categorias, productos_por_categoria, comparativo_por_cadena
from src.charts import barras_precio_cadena
from src.db import is_connected

st.markdown("""
<style>
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
.kpi-sub   { font-size:0.75rem; color:#64748B; }
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("💲 Comparativo de precios por cadena comercial")
st.markdown("Comparativa de precios promedio, mínimo y máximo por cadena, filtrada por producto.")

if not is_connected():
    st.info("ℹ️ Modo demo activo. Se muestran datos de muestra.", icon="ℹ️")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Sidebar: filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtros")

    with st.spinner("Cargando categorías…"):
        categorias = lista_categorias()

    categoria_sel = st.selectbox(
        "Categoría",
        options=["(todas)"] + categorias,
        index=0,
    )

    with st.spinner("Cargando productos…"):
        if categoria_sel == "(todas)":
            from src.queries import lista_productos
            productos = lista_productos()
        else:
            productos = productos_por_categoria(categoria_sel)

    if not productos:
        st.warning("No hay productos disponibles.")
        st.stop()

    # Sugerencia de producto popular
    idx_default = 0
    for i, p in enumerate(productos):
        if "LECHE" in p.upper():
            idx_default = i
            break

    producto_sel = st.selectbox("Producto", options=productos, index=idx_default)

# ─── Consulta y visualización ─────────────────────────────────────────────────
with st.spinner(f"Consultando precios de «{producto_sel}»…"):
    df = comparativo_por_cadena(producto_sel)

if df.empty:
    st.warning(f"No se encontraron datos para el producto seleccionado: **{producto_sel}**")
    st.stop()

# KPIs rápidos
st.markdown(f"### 📦 {producto_sel}")
k1, k2, k3, k4 = st.columns(4)
precio_min = df["precio_minimo"].min()
precio_max = df["precio_maximo"].max()
precio_prom = df["precio_promedio"].mean()
num_cadenas = len(df)

for col, valor, label in [
    (k1, f"${precio_prom:,.2f}", "Precio promedio general"),
    (k2, f"${precio_min:,.2f}",  "Precio mínimo"),
    (k3, f"${precio_max:,.2f}",  "Precio máximo"),
    (k4, f"{num_cadenas}",       "Cadenas con datos"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-valor">{valor}</p>
            <p class="kpi-label">{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Gráfica
fig = barras_precio_cadena(df, producto_sel)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Tabla detallada
st.markdown("### 📋 Detalle por cadena comercial")
df_tabla = df.copy()
df_tabla["precio_promedio"] = df_tabla["precio_promedio"].apply(lambda v: f"${v:,.2f}")
df_tabla["precio_minimo"]   = df_tabla["precio_minimo"].apply(lambda v:   f"${v:,.2f}")
df_tabla["precio_maximo"]   = df_tabla["precio_maximo"].apply(lambda v:   f"${v:,.2f}")
df_tabla["num_registros"]   = df_tabla["num_registros"].apply(lambda v:   f"{int(v):,}")
df_tabla.columns = ["Cadena comercial", "Precio promedio", "Precio mínimo", "Precio máximo", "Registros"]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)
