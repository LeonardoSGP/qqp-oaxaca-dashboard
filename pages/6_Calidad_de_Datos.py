"""
pages/6_Calidad_de_Datos.py
─────────────────────────────────────────────────────────────────────────────
Página 6: Calidad de datos.
Muestra métricas de nulos, duplicados y coordenadas fuera de rango,
combinando datos del JSON del ETL y consultas en vivo a MySQL.
"""

import streamlit as st
import pandas as pd
from src.etl_info import resumen_general
from src.db import is_connected
from src.charts import barras_calidad_nulos

st.markdown("""
<style>
.separador { border:none; border-top:1px solid #2D3748; margin:1.5rem 0; }
.kpi-card  { background:#1A1F2E; border:1px solid #2D3748; border-radius:12px; padding:1.2rem 1.5rem; text-align:center; }
.kpi-valor { font-size:2rem; font-weight:700; color:#2DD4BF; margin:0; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:0.25rem; }
.kpi-sub   { font-size:0.75rem; color:#64748B; }
.badge-ok  { color:#34D399; font-weight:700; }
.badge-warn{ color:#F59E0B; font-weight:700; }
.badge-err { color:#F87171; font-weight:700; }
</style>
""", unsafe_allow_html=True)

st.title("Calidad de datos")
st.markdown("Análisis de la calidad del dataset: valores nulos, duplicados, coordenadas fuera de rango y anomalías de precio.")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

resumen = resumen_general()

# ─── KPIs de calidad ─────────────────────────────────────────────────────────
st.markdown("### Resumen de calidad (desde el proceso ETL)")
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, f"{resumen['rechazados_por_error']}",           "Rechazados por error",        "0 = excelente",          "ok"),
    (k2, f"{resumen['identicos_eliminados']}",           "Duplicados exactos",          "Eliminados del dataset", "warn"),
    (k3, f"{resumen['coordenadas_en_nulo']}",            "Coordenadas en nulo",         "De 191,903 registros",   "warn"),
    (k4, f"{resumen['llaves_repetidas_precio_distinto']}","Llaves con precio distinto", "Mismo prod+est+fecha",   "warn"),
    (k5, f"{resumen['precios_atipicos']}",               "Precios atípicos",            "Detectados en ETL",      "warn"),
]
for col, valor, label, sub, tipo in kpis:
    with col:
        color = "#34D399" if tipo == "ok" else "#F59E0B"
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid {color};">
            <p class="kpi-valor" style="color:{color};">{valor}</p>
            <p class="kpi-label">{label}</p>
            <p class="kpi-sub">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Análisis de completitud por etapa ───────────────────────────────────────
st.markdown("### Completitud por etapa del ETL")
etapas = pd.DataFrame([
    {"Etapa": "Filas leídas (nacional)",      "Registros": resumen["filas_leidas"],      "% completitud": 100.0},
    {"Etapa": "Filtrados (Oaxaca)",           "Registros": resumen["oaxaca"],            "% completitud": round(resumen["oaxaca"]/resumen["filas_leidas"]*100, 4)},
    {"Etapa": "Sin duplicados exactos",       "Registros": resumen["oaxaca"] - resumen["identicos_eliminados"], "% completitud": round((resumen["oaxaca"]-resumen["identicos_eliminados"])/resumen["oaxaca"]*100,2)},
    {"Etapa": "Cargados en MySQL (finales)",  "Registros": resumen["finales"],           "% completitud": round(resumen["finales"]/resumen["oaxaca"]*100,2)},
])
etapas["Registros"] = etapas["Registros"].apply(lambda v: f"{v:,}")
etapas["% completitud"] = etapas["% completitud"].apply(lambda v: f"{v:.4f}%")
st.dataframe(etapas, use_container_width=True, hide_index=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Nulos en MySQL (si conectado) ───────────────────────────────────────────
st.markdown("### Valores nulos en el Data Warehouse (MySQL)")
if not is_connected():
    st.info("Modo demo activo. Conecta MySQL para ver el análisis de nulos en tiempo real.")

    # Fallback con datos conocidos del ETL
    df_nulos_demo = pd.DataFrame([
        {"tabla": "dim_establecimiento", "columna": "latitud",  "nulos": 940,  "total": 51},
        {"tabla": "dim_establecimiento", "columna": "longitud", "nulos": 940,  "total": 51},
        {"tabla": "fact_precio",         "columna": "precio",   "nulos": 0,    "total": 191895},
        {"tabla": "dim_producto",        "columna": "marca",    "nulos": 0,    "total": 3265},
    ])
    fig_nulos = barras_calidad_nulos(df_nulos_demo)
    st.plotly_chart(fig_nulos, use_container_width=True)
    st.caption("Nota: Datos estimados desde el resumen del ETL, no consultados en tiempo real.")
else:
    from src.queries import calidad_nulos_dw, coordenadas_fuera_oaxaca
    with st.spinner("Consultando nulos en MySQL…"):
        df_nulos = calidad_nulos_dw()
        fuera    = coordenadas_fuera_oaxaca()

    if not df_nulos.empty:
        fig_nulos = barras_calidad_nulos(df_nulos)
        st.plotly_chart(fig_nulos, use_container_width=True)

        df_nulos_tabla = df_nulos.copy()
        df_nulos_tabla["pct_nulos"] = (df_nulos_tabla["nulos"] / df_nulos_tabla["total"] * 100).round(2)
        df_nulos_tabla["nulos"]     = df_nulos_tabla["nulos"].apply(lambda v: f"{v:,}")
        df_nulos_tabla["total"]     = df_nulos_tabla["total"].apply(lambda v: f"{v:,}")
        df_nulos_tabla["pct_nulos"] = df_nulos_tabla["pct_nulos"].apply(lambda v: f"{v:.2f}%")
        df_nulos_tabla.columns      = ["Tabla", "Columna", "Nulos", "Total", "% Nulos"]
        st.dataframe(df_nulos_tabla, use_container_width=True, hide_index=True)

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)
    st.markdown("### Coordenadas fuera del bounding box de Oaxaca")
    if fuera == 0:
        st.success("No se detectaron coordenadas fuera del estado de Oaxaca.")
    else:
        st.warning(f"**{fuera}** establecimiento(s) con coordenadas fuera del bounding box de Oaxaca (lat 15.6–18.2, lon -98.6–-93.6).")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ─── Notas de calidad ────────────────────────────────────────────────────────
st.markdown("### Notas y observaciones")
st.markdown("""
| Métrica | Valor | Interpretación |
|---|---|---|
| Duplicados exactos eliminados | 8 | Muy bajo — datos de buena calidad |
| Coordenadas nulas | 940 | ~0.49% de registros sin geolocalización |
| Llaves repetidas, precio distinto | 6,694 | Mismo producto/establecimiento/fecha con precios diferentes (variación de precio en el día) |
| Precios atípicos detectados | 1 | Dato extremo conservado en la carga |
| Registros rechazados por error | 0 | 100% de los registros filtrados pudieron procesarse |

> **Conclusión:** El dataset presenta una calidad alta. La mayor área de mejora
> es la geolocalización (940 registros sin coordenadas), que limita el mapa a
> los establecimientos con datos completos.
""")
