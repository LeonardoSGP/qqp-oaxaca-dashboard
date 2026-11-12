"""
pages/1_Carga_de_datos_ETL.py
─────────────────────────────────────────────────────────────────────────────
Página 1: Visualización del proceso ETL.
Muestra el flujo de extracción -> transformación -> carga, KPIs del proceso,
barras de filas por archivo, tabla de reglas de limpieza y sección de
conciliación que compara conteos reales vs esperados en MySQL.
"""

import streamlit as st
import pandas as pd

from src.etl_info import resumen_general, filas_por_archivo, reglas_limpieza, tablas_esperadas
from src.charts import embudo_etl, barras_por_archivo
from src.db import is_connected

# ─── Importar CSS global (re-inyectar en subpáginas) ─────────────────────────
st.markdown("""
<style>
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
.kpi-sub   { font-size:0.75rem; color:#64748B; }
.etl-card  { background:#1A1F2E; border-left:4px solid #2DD4BF; border-radius:8px; padding:1rem 1.2rem; margin-bottom:0.5rem; }
.etl-card.amber { border-left-color:#F59E0B; }
.etl-card.green { border-left-color:#34D399; }
.etl-titulo{ font-size:1rem; font-weight:600; color:#E2E8F0; margin:0 0 0.3rem 0; }
.etl-desc  { font-size:0.82rem; color:#94A3B8; margin:0; }
.badge-ok  { color:#34D399; font-weight:700; }
.badge-err { color:#F87171; font-weight:700; }
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.title("Carga de datos — Proceso ETL")
st.markdown("Resumen del proceso de Extracción, Transformación y Carga de datos del programa *Quién es Quién en los Precios*.")

# ─── Cargar datos ETL ─────────────────────────────────────────────────────────
resumen = resumen_general()

# ─── Tarjetas de flujo ETL ────────────────────────────────────────────────────
st.markdown("### Etapas del proceso")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="etl-card">
        <p class="etl-titulo">Extracción</p>
        <p class="etl-desc">
            Lectura de <strong>16 archivos CSV</strong> del programa Quién es Quién en los Precios
            (enero–agosto 2026). Total: <strong>9,388,457 filas</strong> a nivel nacional.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="etl-card amber">
        <p class="etl-titulo">Transformación</p>
        <p class="etl-desc">
            Filtro por estado = Oaxaca, eliminación de duplicados exactos, detección de
            coordenadas nulas, llaves repetidas con precio distinto y precios atípicos.
            Resultado: <strong>191,895 registros limpios</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="etl-card green">
        <p class="etl-titulo">Carga</p>
        <p class="etl-desc">
            Carga en MySQL 8: esquema <strong>qqp_oltp</strong> (modelo relacional)
            y esquema <strong>qqp_dw</strong> (modelo en estrella + data mart).
            Duración total: <strong>2 min 38 s</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── KPIs del proceso ─────────────────────────────────────────────────────────
st.markdown("### KPIs del proceso")
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, f"{resumen['archivos']}",                     "Archivos CSV",               "Fuente de datos"),
    (k2, f"{resumen['filas_leidas']:,}",               "Filas leídas",               "Nacional"),
    (k3, f"{resumen['oaxaca']:,}",                     "Filtrados: Oaxaca",          "Antes de limpieza"),
    (k4, f"{resumen['identicos_eliminados']}",         "Duplicados eliminados",      "Registros idénticos"),
    (k5, f"{resumen['finales']:,}",                    "Registros finales",          "Cargados en MySQL"),
    (k6, resumen['duracion'],                           "Duración del ETL",           "Total del proceso"),
]
for col, valor, label, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-valor">{valor}</p>
            <p class="kpi-label">{label}</p>
            <p class="kpi-sub">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

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
st.markdown("### Conciliación de carga (conteos reales vs esperados)")

if not is_connected():
    st.info("Modo demo activo: la conciliación requiere conexión a MySQL.")
else:
    df_esp = tablas_esperadas()
    filas_conc = []

    with st.spinner("Consultando conteos en MySQL…"):
        from src.db import get_engine_dw, get_engine_oltp
        from sqlalchemy import text

        for _, row in df_esp.iterrows():
            tabla_full = row["tabla"]
            esperado   = row["esperado"]
            partes     = tabla_full.split(".")
            esquema    = partes[0].replace("qqp_", "")
            tabla_name = partes[1]

            sql_count  = f"SELECT COUNT(*) FROM {tabla_full}"
            try:
                engine = get_engine_dw() if "dw" in partes[0] else get_engine_oltp()
                with engine.connect() as conn:
                    real = conn.execute(text(sql_count)).scalar()
                diff   = real - esperado
                estado = "OK" if diff == 0 else ("DIFERENCIA" if abs(diff) < 10 else "ERROR")
                diff_str = f"+{diff:,}" if diff > 0 else f"{diff:,}"
            except Exception as e:
                real     = None
                diff_str = "N/A"
                estado   = "ERROR"

            filas_conc.append({
                "Estado": estado,
                "Tabla": tabla_full,
                "Esperado": f"{esperado:,}",
                "Real": f"{real:,}" if real is not None else "Error",
                "Diferencia": diff_str if real is not None else str(e)[:50],
            })

    df_conc = pd.DataFrame(filas_conc)
    st.dataframe(df_conc, use_container_width=True, hide_index=True)

    total_ok  = sum(1 for r in filas_conc if r["Estado"] == "OK")
    total_tot = len(filas_conc)
    if total_ok == total_tot:
        st.success(f"Todas las tablas concilian correctamente ({total_ok}/{total_tot}).")
    else:
        st.warning(f"{total_tot - total_ok} tabla(s) con diferencias. Revisa los datos.")
