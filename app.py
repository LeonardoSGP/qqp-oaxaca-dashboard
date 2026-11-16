"""
app.py
─────────────────────────────────────────────────────────────────────────────
Punto de entrada del dashboard QQP Oaxaca.
Configura la navegación superior (position="top") con diseño Glassmorphism,
verifica la conexión a MySQL y muestra el panel de inicio del sistema.

Proyecto: Quién es Quién en los Precios — Oaxaca 2026
TecNM Campus Oaxaca · Datos abiertos Profeco
"""

import streamlit as st
from src.db import test_connection
from src.theme import apply_glassmorphism, render_top_status_bar

# ─── Configuración global de la página ───────────────────────────────────────
st.set_page_config(
    page_title="QQP Oaxaca · Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Aplicar sistema de diseño Glassmorphism ─────────────────────────────────
apply_glassmorphism()

# ─── Verificación de conexión a MySQL ────────────────────────────────────────
conectado, msg_conexion = test_connection()
render_top_status_bar(conectado, msg_conexion)


# ─── Vista de Inicio ────────────────────────────────────────────────────────
def pagina_inicio():
    st.title("Dashboard — Quién es Quién en los Precios")
    st.markdown("**Oaxaca · Enero–Agosto 2026** | Datos abiertos Profeco")

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        (col1, "9,388,457", "Filas leídas (total nacional)", "16 archivos CSV quincenales"),
        (col2, "191,895",   "Registros de Oaxaca",           "Cargados y validados en MySQL"),
        (col3, "3,265",     "Productos únicos",               "Catálogo dim_producto"),
        (col4, "51",        "Establecimientos",               "Catálogo dim_establecimiento"),
    ]
    for col, valor, label, sub in kpis:
        with col:
            st.markdown(
                f'<div class="kpi-card glass-card"><p class="kpi-valor">{valor}</p>'
                f'<p class="kpi-label">{label}</p><p class="kpi-sub">{sub}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)

    st.markdown("### Páginas del dashboard")
    st.markdown("""
| Página | Descripción |
|---|---|
| **Carga de datos (ETL)** | Flujo de extracción, transformación y carga; KPIs, reglas de limpieza y conciliación en vivo |
| **Data Warehouse** | Modelo en estrella, conteos de tablas y vistas previas paginadas |
| **Comparativo de precios** | Precio promedio por cadena comercial con filtros de producto y categoría |
| **Series de tiempo** | Evolución mensual del precio por producto y cadena |
| **Mapa** | Establecimientos de Oaxaca con coordenadas geográficas |
| **Calidad de datos** | Nulos, duplicados y coordenadas fuera de rango |
| **KPIs – Canasta básica** | Evolución y comparación de precios de los 24 productos Pacic |

Navega usando el **menú superior en el encabezado (header)**.
""")

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)
    st.markdown(
        "**Fuente:** Programa *Quién es Quién en los Precios* · "
        "[Profeco](https://www.gob.mx/profeco)  "
        "| **Autores:** Leonardo Garcia y Cristian Placido · TecNM Campus Oaxaca"
    )


# ─── Configuración de navegación nativa en la parte superior del header ─────
pg = st.navigation(
    [
        st.Page(pagina_inicio, title="Inicio", default=True),
        st.Page("pages/1_Carga_de_datos_ETL.py", title="Carga de datos (ETL)"),
        st.Page("pages/2_Data_Warehouse.py", title="Data Warehouse"),
        st.Page("pages/3_Comparativo_de_Precios.py", title="Comparativo de precios"),
        st.Page("pages/4_Series_de_Tiempo.py", title="Series de tiempo"),
        st.Page("pages/5_Mapa.py", title="Mapa"),
        st.Page("pages/6_Calidad_de_Datos.py", title="Calidad de datos"),
        st.Page("pages/7_KPIs_canasta_basica.py", title="KPIs – Canasta básica"),
    ],
    position="top",
)

pg.run()
