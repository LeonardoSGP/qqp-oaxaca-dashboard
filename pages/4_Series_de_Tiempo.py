"""
pages/4_Series_de_Tiempo.py
─────────────────────────────────────────────────────────────────────────────
Página 4: Evolución mensual del precio promedio con diseño Glassmorphism.
Selector de producto y multiselector de cadenas comerciales integrados.
"""

import streamlit as st
from src.queries import lista_categorias, productos_por_categoria, lista_productos, lista_cadenas, serie_tiempo_producto
from src.charts import linea_serie_tiempo
from src.theme import apply_glassmorphism

apply_glassmorphism()

st.title("Series de tiempo — Evolución mensual de precios")
st.markdown("Visualiza cómo cambia el precio promedio de un producto mes a mes por cadena comercial.")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Filtros superiores ──────────────────────────────────────────────────────
f_col1, f_col2 = st.columns([1, 2])

with f_col1:
    categorias = lista_categorias()
    categoria_sel = st.selectbox("Categoría", ["(todas)"] + categorias)

with f_col2:
    if categoria_sel == "(todas)":
        productos = lista_productos()
    else:
        productos = productos_por_categoria(categoria_sel)

    if not productos:
        st.warning("No hay productos disponibles.")
        st.stop()

    idx_default = 0
    for i, p in enumerate(productos):
        if "LECHE" in p.upper():
            idx_default = i
            break

    producto_sel = st.selectbox("Producto", options=productos, index=idx_default)

cadenas = lista_cadenas()
cadenas_sel = st.multiselect(
    "Cadenas comerciales",
    options=cadenas,
    default=cadenas[:5] if len(cadenas) >= 5 else cadenas,
    help="Selecciona una o más cadenas para comparar.",
)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Consulta y gráfica ───────────────────────────────────────────────────────
if not cadenas_sel:
    st.warning("Selecciona al menos una cadena comercial.")
    st.stop()

with st.spinner(f"Cargando series para «{producto_sel}»…"):
    df = serie_tiempo_producto(producto_sel, cadenas_sel)

if df.empty:
    st.warning("No hay datos para la combinación seleccionada.")
    st.stop()

# KPIs globales del producto con tamaño de referencia unificado
precio_prom     = df["precio_promedio"].mean()
precio_min      = df["precio_promedio"].min()
precio_max      = df["precio_promedio"].max()
meses_con_datos = df["mes"].nunique()

k1, k2, k3, k4 = st.columns(4)
for col, valor, label, sub in [
    (k1, f"${precio_prom:,.2f}", "Precio promedio global", "Media del periodo"),
    (k2, f"${precio_min:,.2f}",  "Mínimo mensual",         "Menor promedio registrado"),
    (k3, f"${precio_max:,.2f}",  "Máximo mensual",         "Mayor promedio registrado"),
    (k4, f"{meses_con_datos}",   "Meses con datos",        "Enero–Agosto 2026"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card glass-card"><p class="kpi-valor">{valor}</p>'
            f'<p class="kpi-label">{label}</p><p class="kpi-sub">{sub}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Gráfica de líneas
fig = linea_serie_tiempo(df, producto_sel)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Tabla
st.markdown("### Datos mensuales")
df_tabla = df.pivot_table(
    index="cadena_comercial",
    columns="mes",
    values="precio_promedio",
    aggfunc="first",
).reset_index()
df_tabla.columns = ["Cadena comercial"] + [f"Mes {c}" for c in df_tabla.columns[1:]]
st.dataframe(df_tabla.round(2), use_container_width=True, hide_index=True)
