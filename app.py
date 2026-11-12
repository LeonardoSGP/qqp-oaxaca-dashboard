"""
app.py
─────────────────────────────────────────────────────────────────────────────
Punto de entrada del dashboard QQP Oaxaca.
Configura la página principal, verifica la conexión a MySQL y muestra
el estado de la conexión en la barra lateral.

Proyecto: Quién es Quién en los Precios — Oaxaca 2026
TecNM Campus Oaxaca · Datos abiertos Profeco (CC BY 4.0)
"""

import streamlit as st
from src.db import test_connection

# ─── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="QQP Oaxaca · Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* Tarjetas KPI */
.kpi-card {
    background: #1A1F2E;
    border: 1px solid #2D3748;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.kpi-valor {
    font-size: 2rem;
    font-weight: 700;
    color: #2DD4BF;
    margin: 0;
}
.kpi-label {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 0.25rem;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #64748B;
}

/* Tarjetas de paso ETL */
.etl-card {
    background: #1A1F2E;
    border-left: 4px solid #2DD4BF;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.etl-card.amber { border-left-color: #F59E0B; }
.etl-card.green { border-left-color: #34D399; }
.etl-titulo {
    font-size: 1rem;
    font-weight: 600;
    color: #E2E8F0;
    margin: 0 0 0.3rem 0;
}
.etl-desc {
    font-size: 0.82rem;
    color: #94A3B8;
    margin: 0;
}

/* Badges de conciliación */
.badge-ok  { color: #34D399; font-weight: 700; }
.badge-err { color: #F87171; font-weight: 700; }

/* Separador */
.separador {
    border: none;
    border-top: 1px solid #2D3748;
    margin: 1.5rem 0;
}

/* Ocultar el texto "app" en el sidebar */
[data-testid="stSidebarNav"] li:first-child { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Verificación de conexión (cacheada) ─────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def _estado_conexion():
    return test_connection()

conectado, msg_conexion = _estado_conexion()

# ─── Sidebar: estado de conexión ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 QQP Oaxaca")
    st.markdown("**Quién es Quién en los Precios**")
    st.markdown("TecNM Campus Oaxaca · 2026")
    st.markdown("<hr class='separador'>", unsafe_allow_html=True)

    if conectado:
        st.success(f"✅ Conectado · {msg_conexion}", icon="🟢")
    else:
        st.warning("⚠️ **Modo demo activo**\n\nNo se detectó conexión a MySQL. Se muestran datos de muestra.", icon="🟡")

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)
    st.caption("Datos: Profeco · CC BY 4.0")
    st.caption("Enero–Agosto 2026 · Oaxaca")

# ─── Página de inicio ────────────────────────────────────────────────────────
st.title("🛒 Dashboard — Quién es Quién en los Precios")
st.markdown("**Oaxaca · Enero–Agosto 2026** | Datos abiertos Profeco (CC BY 4.0)")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
kpis = [
    (col1, "9,388,457", "Filas leídas (total nacional)", "16 archivos CSV"),
    (col2, "191,895",   "Registros de Oaxaca",           "Cargados en MySQL"),
    (col3, "3,265",     "Productos únicos",               "dim_producto"),
    (col4, "51",        "Establecimientos",               "dim_establecimiento"),
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

st.markdown("### 📂 Páginas del dashboard")
st.markdown("""
| Página | Descripción |
|---|---|
| 🔄 **Carga de datos (ETL)** | Flujo de extracción, transformación y carga; KPIs, reglas de limpieza y conciliación en vivo |
| 🗄️ **Data Warehouse** | Modelo en estrella, conteos de tablas y vistas previas paginadas |
| 💲 **Comparativo de precios** | Precio promedio por cadena comercial con filtros de producto y categoría |
| 📈 **Series de tiempo** | Evolución mensual del precio por producto y cadena |
| 🗺️ **Mapa** | Establecimientos de Oaxaca con coordenadas geográficas |
| 🔍 **Calidad de datos** | Nulos, duplicados y coordenadas fuera de rango |

Navega usando el menú de la **barra lateral izquierda** ☰.
""")

st.markdown("<hr class='separador'>", unsafe_allow_html=True)
st.markdown(
    "**Fuente:** Programa *Quién es Quién en los Precios* · "
    "[Profeco](https://www.gob.mx/profeco) · "
    "Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es)  "
    "| **Autor:** Leonardo Sadot García Pino · TecNM Campus Oaxaca"
)
