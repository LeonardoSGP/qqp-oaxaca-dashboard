"""
pages/1_Carga_de_datos_ETL.py
─────────────────────────────────────────────────────────────────────────────
Página 1: Visualización del proceso ETL con diseño Glassmorphism.
Muestra el flujo de extracción -> transformación -> carga, KPIs del proceso,
barras de filas por archivo, tabla de reglas de limpieza y sección de
conciliación que compara conteos reales vs esperados en MySQL.
"""

import streamlit as st

from src.etl_info import resumen_general, filas_por_archivo, reglas_limpieza
from src.charts import embudo_etl, barras_por_archivo
from src.queries import conciliacion_tablas
from src.theme import apply_glassmorphism

apply_glassmorphism()

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.title("Carga de datos — Proceso ETL")
st.markdown("Resumen del proceso de Extracción, Transformación y Carga de datos del programa *Quién es Quién en los Precios*.")

# ─── Cargar datos ETL ─────────────────────────────────────────────────────────
resumen = resumen_general()

# ─── Tarjetas de flujo ETL (Referencia de altura máxima para todas las cards) ─
st.markdown("### Etapas del proceso")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="etl-card glass-card">'
        '<p class="etl-titulo">Extracción</p>'
        '<p class="etl-desc">Lectura de <strong>16 archivos CSV</strong> del programa Quién es Quién en los Precios '
        '(enero–agosto 2026). Total: <strong>9,388,457 filas</strong> a nivel nacional.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        '<div class="etl-card glass-card amber">'
        '<p class="etl-titulo">Transformación</p>'
        '<p class="etl-desc">Filtro por estado = Oaxaca, eliminación de duplicados exactos, detección de '
        'coordenadas nulas, llaves repetidas con precio distinto y precios atípicos. '
        'Resultado: <strong>191,895 registros limpios</strong>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        '<div class="etl-card glass-card green">'
        '<p class="etl-titulo">Carga</p>'
        '<p class="etl-desc">Carga en MySQL 8: esquema <strong>qqp_oltp</strong> (modelo relacional) '
        'y esquema <strong>qqp_dw</strong> (modelo en estrella + data mart). '
        'Duración total: <strong>2 min 38 s</strong>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── KPIs del proceso ─────────────────────────────────────────────────────────
st.markdown("### KPIs del proceso")
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, f"{resumen['archivos']}",             "Archivos CSV",          "Fuente de datos"),
    (k2, f"{resumen['filas_leidas']:,}",       "Filas leídas",          "Nacional"),
    (k3, f"{resumen['oaxaca']:,}",             "Filtrados: Oaxaca",     "Antes de limpieza"),
    (k4, f"{resumen['identicos_eliminados']}", "Duplicados eliminados", "Registros idénticos"),
    (k5, f"{resumen['finales']:,}",            "Registros finales",     "Cargados en MySQL"),
    (k6, resumen['duracion'],                  "Duración del ETL",      "Total del proceso"),
]
for col, valor, label, sub in kpis:
    with col:
        st.markdown(
            f'<div class="kpi-card glass-card"><p class="kpi-valor">{valor}</p>'
            f'<p class="kpi-label">{label}</p><p class="kpi-sub">{sub}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Embudo + Barras por archivo ─────────────────────────────────────────────
col_emb, col_bar = st.columns([1, 1.4])

with col_emb:
    st.markdown("### Flujo de filas")
    fig_emb = embudo_etl(resumen["filas_leidas"], resumen["oaxaca"], resumen["finales"])
    st.plotly_chart(fig_emb, use_container_width=True)

with col_bar:
    st.markdown("### Filas por archivo CSV")
    df_arch = filas_por_archivo()
    fig_bar = barras_por_archivo(df_arch)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Reglas de limpieza ───────────────────────────────────────────────────────
st.markdown("### Reglas de limpieza aplicadas")
df_reglas = reglas_limpieza()
df_reglas.columns = ["Regla de limpieza", "Cantidad"]
df_reglas["Cantidad"] = df_reglas["Cantidad"].apply(lambda v: f"{v:,}")
st.dataframe(
    df_reglas,
    use_container_width=True,
    hide_index=True,
)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Conciliación en vivo ─────────────────────────────────────────────────────
st.markdown("### Conciliación de carga (conteos reales en MySQL vs esperados)")

with st.spinner("Consultando conteos en MySQL…"):
    df_conc = conciliacion_tablas()

st.dataframe(df_conc, use_container_width=True, hide_index=True)

total_ok  = int((df_conc["Estado"] == "OK").sum()) if not df_conc.empty else 0
total_tot = len(df_conc)
if total_ok == total_tot and total_tot > 0:
    st.success(f"Todas las tablas concilian correctamente ({total_ok}/{total_tot}).")
else:
    st.warning(f"{total_tot - total_ok} tabla(s) con diferencias. Revisa los datos.")
