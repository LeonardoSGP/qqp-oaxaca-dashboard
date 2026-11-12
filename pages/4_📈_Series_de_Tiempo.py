"""
pages/4_📈_Series_de_Tiempo.py
─────────────────────────────────────────────────────────────────────────────
Página 4: Evolución mensual del precio promedio.
Selector de producto y multiselector de cadenas comerciales.
"""

import streamlit as st
from src.queries import lista_categorias, productos_por_categoria, lista_productos, lista_cadenas, serie_tiempo_producto
from src.charts import linea_serie_tiempo
from src.db import is_connected

st.markdown("""
<style>
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Series de tiempo — Evolución mensual de precios")
st.markdown("Visualiza cómo cambia el precio promedio de un producto mes a mes por cadena comercial.")

if not is_connected():
    st.info("ℹ️ Modo demo activo. Se muestran datos de muestra.", icon="ℹ️")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Sidebar: filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtros")

    categorias = lista_categorias()
    categoria_sel = st.selectbox("Categoría", ["(todas)"] + categorias)

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

# ─── Consulta y gráfica ───────────────────────────────────────────────────────
if not cadenas_sel:
    st.warning("Selecciona al menos una cadena comercial en el panel lateral.")
    st.stop()

with st.spinner(f"Cargando series para «{producto_sel}»…"):
    df = serie_tiempo_producto(producto_sel, cadenas_sel)

if df.empty:
    st.warning("No hay datos para la combinación seleccionada.")
    st.stop()

# KPIs globales del producto
precio_prom = df["precio_promedio"].mean()
precio_min  = df["precio_promedio"].min()
precio_max  = df["precio_promedio"].max()
meses_con_datos = df["mes"].nunique()

k1, k2, k3, k4 = st.columns(4)
for col, valor, label in [
    (k1, f"${precio_prom:,.2f}", "Precio promedio global"),
    (k2, f"${precio_min:,.2f}",  "Mínimo mensual"),
    (k3, f"${precio_max:,.2f}",  "Máximo mensual"),
    (k4, f"{meses_con_datos}",   "Meses con datos"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-valor">{valor}</p>
            <p class="kpi-label">{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Gráfica de líneas
fig = linea_serie_tiempo(df, producto_sel)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# Tabla de datos
st.markdown("### 📋 Datos de la serie")
df_tabla = df.copy()
df_tabla["precio_promedio"] = df_tabla["precio_promedio"].apply(lambda v: f"${v:,.2f}")
df_tabla["num_registros"]   = df_tabla["num_registros"].apply(lambda v: f"{int(v):,}")
df_tabla.columns = ["Mes", "Cadena comercial", "Precio promedio", "Registros"]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)
