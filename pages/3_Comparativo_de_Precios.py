"""
pages/3_Comparativo_de_Precios.py
─────────────────────────────────────────────────────────────────────────────
Página 3: Comparativo de precios por cadena comercial con diseño Glassmorphism.
Filtros integrados en el panel superior (categoría y producto); gráfica de barras
de precio promedio y tabla con mínimo, máximo y número de registros.
"""

import streamlit as st
from src.queries import lista_categorias, lista_productos, productos_por_categoria, comparativo_por_cadena
from src.charts import barras_precio_cadena
from src.theme import apply_glassmorphism

apply_glassmorphism()

st.title("Comparativo de precios por cadena comercial")
st.markdown("Comparativa de precios promedio, mínimo y máximo por cadena, filtrada por producto.")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Filtros superiores en panel Glassmorphism ───────────────────────────────
f_col1, f_col2 = st.columns([1, 2])

with f_col1:
    with st.spinner("Cargando categorías…"):
        categorias = lista_categorias()
    categoria_sel = st.selectbox(
        "Categoría",
        options=["(todas)"] + categorias,
        index=0,
    )

with f_col2:
    with st.spinner("Cargando productos…"):
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

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Consulta y visualización ─────────────────────────────────────────────────
with st.spinner(f"Consultando precios de «{producto_sel}»…"):
    df = comparativo_por_cadena(producto_sel)

if df.empty:
    st.warning(f"No se encontraron datos para el producto seleccionado: **{producto_sel}**")
    st.stop()

# KPIs rápidos con tamaño de referencia unificado
st.markdown(f"### {producto_sel}")
k1, k2, k3, k4 = st.columns(4)
precio_min  = df["precio_minimo"].min()
precio_max  = df["precio_maximo"].max()
precio_prom = df["precio_promedio"].mean()
num_cadenas = len(df)

for col, valor, label, sub in [
    (k1, f"${precio_prom:,.2f}", "Precio promedio general", "Media en Oaxaca"),
    (k2, f"${precio_min:,.2f}",  "Precio mínimo",           "Opción más económica"),
    (k3, f"${precio_max:,.2f}",  "Precio máximo",           "Cota superior"),
    (k4, f"{num_cadenas}",       "Cadenas con datos",       "Supermercados comparados"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card glass-card"><p class="kpi-valor">{valor}</p>'
            f'<p class="kpi-label">{label}</p><p class="kpi-sub">{sub}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Gráfica
fig = barras_precio_cadena(df, producto_sel)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Tabla detallada
st.markdown("### Detalle por cadena comercial")
df_mostrar = df[["cadena_comercial", "precio_promedio", "precio_minimo", "precio_maximo", "num_registros"]].copy()
df_mostrar["precio_promedio"] = df_mostrar["precio_promedio"].apply(lambda v: f"${v:,.2f}")
df_mostrar["precio_minimo"]   = df_mostrar["precio_minimo"].apply(lambda v: f"${v:,.2f}")
df_mostrar["precio_maximo"]   = df_mostrar["precio_maximo"].apply(lambda v: f"${v:,.2f}")
df_mostrar["num_registros"]   = df_mostrar["num_registros"].apply(lambda v: f"{v:,}")
df_mostrar.columns = ["Cadena comercial", "Precio promedio", "Precio mínimo", "Precio máximo", "Registros"]
st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
