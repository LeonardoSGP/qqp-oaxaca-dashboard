"""
src/charts.py
─────────────────────────────────────────────────────────────────────────────
Funciones reutilizables para generar gráficas Plotly con la paleta del
dashboard. Tema consistente: fondo oscuro, acentos teal (#2DD4BF) y
ámbar (#F59E0B).
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── Paleta y tema base ──────────────────────────────────────────────────────
FONDO       = "#0E1117"
FONDO2      = "#1A1F2E"
TEAL        = "#2DD4BF"
AMBER       = "#F59E0B"
SLATE       = "#94A3B8"
TEXTO       = "#E2E8F0"
PALETA      = [
    "#2DD4BF", "#F59E0B", "#60A5FA", "#F472B6",
    "#34D399", "#A78BFA", "#FB923C", "#38BDF8",
]

_LAYOUT_BASE = dict(
    paper_bgcolor=FONDO,
    plot_bgcolor=FONDO2,
    font=dict(family="Inter, sans-serif", color=TEXTO, size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor=FONDO2, bordercolor="#2D3748", borderwidth=1),
)


def _aplicar_tema(fig: go.Figure, titulo: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=TEXTO), x=0.0),
        xaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", tickcolor=SLATE),
        yaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", tickcolor=SLATE),
        **_LAYOUT_BASE,
    )
    return fig


# ─── Embudo ETL ──────────────────────────────────────────────────────────────
def embudo_etl(filas_leidas: int, oaxaca: int, finales: int) -> go.Figure:
    """Gráfica de embudo mostrando el flujo de filas del proceso ETL."""
    fig = go.Figure(go.Funnel(
        y=["Filas leídas", "Registros Oaxaca", "Cargados en MySQL"],
        x=[filas_leidas, oaxaca, finales],
        textinfo="value+percent initial",
        textfont=dict(color=TEXTO, size=14),
        marker=dict(color=[TEAL, AMBER, "#34D399"]),
        connector=dict(line=dict(color="#2D3748", width=2)),
    ))
    fig.update_layout(
        title=dict(text="Flujo de datos: Extracción → Carga", font=dict(size=16, color=TEXTO)),
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO2,
        font=dict(color=TEXTO),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# ─── Barras: filas por archivo ───────────────────────────────────────────────
def barras_por_archivo(df: pd.DataFrame) -> go.Figure:
    """Barras horizontales de filas leídas por archivo CSV."""
    df = df.sort_values("filas")
    fig = go.Figure(go.Bar(
        y=df["archivo"],
        x=df["filas"],
        orientation="h",
        marker_color=TEAL,
        text=df["filas"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, "Filas leídas por archivo CSV")
    fig.update_layout(height=480)
    fig.update_yaxes(tickfont=dict(size=11))
    return fig


# ─── Barras: comparativo de precios por cadena ───────────────────────────────
def barras_precio_cadena(df: pd.DataFrame, producto: str) -> go.Figure:
    """Barras de precio promedio por cadena comercial."""
    df = df.sort_values("precio_promedio")
    fig = go.Figure(go.Bar(
        x=df["precio_promedio"],
        y=df["cadena_comercial"],
        orientation="h",
        marker_color=TEAL,
        text=df["precio_promedio"].apply(lambda v: f"${v:,.2f}"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, f"Precio promedio por cadena — {producto}")
    fig.update_layout(height=max(350, len(df) * 38))
    return fig


# ─── Líneas: serie de tiempo ─────────────────────────────────────────────────
def linea_serie_tiempo(df: pd.DataFrame, producto: str) -> go.Figure:
    """Evolución mensual del precio promedio por cadena."""
    fig = go.Figure()
    cadenas = df["cadena_comercial"].unique()
    for i, cadena in enumerate(cadenas):
        sub = df[df["cadena_comercial"] == cadena].sort_values("mes")
        fig.add_trace(go.Scatter(
            x=sub["mes"],
            y=sub["precio_promedio"],
            mode="lines+markers",
            name=cadena,
            line=dict(color=PALETA[i % len(PALETA)], width=2),
            marker=dict(size=6),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Mes: %{x}<br>"
                "Precio: $%{y:,.2f}<extra></extra>"
            ),
        ))
    _aplicar_tema(fig, f"Evolución mensual de precio — {producto}")
    fig.update_xaxes(title_text="Mes")
    fig.update_yaxes(title_text="Precio promedio (MXN)", tickprefix="$")
    return fig


# ─── Mapa de establecimientos ────────────────────────────────────────────────
def mapa_establecimientos(df: pd.DataFrame) -> go.Figure:
    """Mapa de burbujas de establecimientos en Oaxaca."""
    max_reg = df["num_registros"].max() if not df.empty else 1
    fig = go.Figure(go.Scattermapbox(
        lat=df["latitud"],
        lon=df["longitud"],
        mode="markers",
        marker=dict(
            size=df["num_registros"].apply(lambda v: 6 + (v / max_reg) * 20),
            color=df["num_registros"],
            colorscale=[[0, "#1A1F2E"], [0.5, AMBER], [1, TEAL]],
            colorbar=dict(
                title="Registros",
                titlefont=dict(color=TEXTO),
                tickfont=dict(color=TEXTO),
            ),
            opacity=0.85,
        ),
        text=df.apply(
            lambda r: (
                f"<b>{r['nombre_comercial']}</b><br>"
                f"Cadena: {r['cadena_comercial']}<br>"
                f"Municipio: {r['municipio']}<br>"
                f"Registros: {r['num_registros']:,}"
            ),
            axis=1,
        ),
        hoverinfo="text",
    ))
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=17.0, lon=-96.7),
            zoom=6,
        ),
        paper_bgcolor=FONDO,
        font=dict(color=TEXTO),
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
    )
    return fig


# ─── Barras: conteo de tablas DW ─────────────────────────────────────────────
def barras_conteo_tablas(df: pd.DataFrame) -> go.Figure:
    """Barras de conteo de filas por tabla del Data Warehouse."""
    df = df.sort_values("filas", ascending=False)
    colores = [TEAL if "fact" in t else AMBER for t in df["tabla"]]
    fig = go.Figure(go.Bar(
        x=df["tabla"],
        y=df["filas"],
        marker_color=colores,
        text=df["filas"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, "Filas por tabla en el Data Warehouse")
    fig.update_xaxes(tickangle=-15)
    fig.update_yaxes(title_text="Número de filas")
    return fig


# ─── Barras: calidad de datos (nulos) ────────────────────────────────────────
def barras_calidad_nulos(df: pd.DataFrame) -> go.Figure:
    """Barras de valores nulos por columna."""
    df = df.copy()
    df["etiqueta"] = df["tabla"] + "." + df["columna"]
    df["pct"] = (df["nulos"] / df["total"] * 100).round(2)
    fig = go.Figure(go.Bar(
        x=df["etiqueta"],
        y=df["pct"],
        marker_color=AMBER,
        text=df["pct"].apply(lambda v: f"{v:.2f}%"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, "Porcentaje de valores nulos por columna")
    fig.update_yaxes(title_text="% Nulos", range=[0, max(df["pct"].max() * 1.3, 1)])
    return fig
