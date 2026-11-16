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

# ─── Paleta y tema base (Glassmorphism translúcido) ──────────────────────────
FONDO       = "rgba(15, 23, 42, 0.35)"
FONDO2      = "rgba(30, 41, 59, 0.45)"
TEAL        = "#2DD4BF"
AMBER       = "#F59E0B"
SLATE       = "#94A3B8"
TEXTO       = "#F8FAFC"
PALETA      = [
    "#2DD4BF", "#F59E0B", "#60A5FA", "#F472B6",
    "#34D399", "#A78BFA", "#FB923C", "#38BDF8",
]

_LAYOUT_BASE = dict(
    paper_bgcolor=FONDO,
    plot_bgcolor=FONDO2,
    font=dict(family="Outfit, Inter, sans-serif", color=TEXTO, size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(15, 23, 42, 0.65)", bordercolor="rgba(255, 255, 255, 0.18)", borderwidth=1),
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
def mapa_establecimientos(
    df: pd.DataFrame,
    estilo: str = "open-street-map",
    zoom: float = 12.3,
) -> go.Figure:
    """Mapa de burbujas de establecimientos en Oaxaca."""
    import os
    from dotenv import load_dotenv
    if not os.getenv("MAPBOX_TOKEN", "").strip():
        load_dotenv(override=True)
    mapbox_token = os.getenv("MAPBOX_TOKEN", "").strip()

    max_reg = df["num_registros"].max() if not df.empty else 1
    center_lat = float(df["latitud"].mean()) if not df.empty else 17.065
    center_lon = float(df["longitud"].mean()) if not df.empty else -96.715

    # Si hay token de Mapbox y se usa un estilo propio de Mapbox, usar Scattermapbox/mapbox
    # (ya que layout.map de MapLibre en Plotly 6+ no acepta la propiedad 'accesstoken').
    estilos_mapbox = {"streets", "dark", "satellite-streets", "satellite", "outdoors", "light", "basic"}
    usar_mapbox = bool(mapbox_token and estilo in estilos_mapbox and hasattr(go, "Scattermapbox"))

    if usar_mapbox:
        ScatterCls = go.Scattermapbox
        map_layout_key = "mapbox"
    else:
        ScatterCls = getattr(go, "Scattermap", None) or getattr(go, "Scattermapbox", None)
        map_layout_key = "map" if hasattr(go, "Scattermap") else "mapbox"

    fig = go.Figure(ScatterCls(
        lat=df["latitud"],
        lon=df["longitud"],
        mode="markers",
        marker=dict(
            size=df["num_registros"].apply(lambda v: 10 + (v / max_reg) * 18),
            color=df["num_registros"],
            colorscale=[[0, "#38BDF8"], [0.5, AMBER], [1, TEAL]],
            colorbar=dict(
                title=dict(text="Registros", font=dict(color=TEXTO)),
                tickfont=dict(color=TEXTO),
                y=0.45,
                len=0.72,
                thickness=18,
            ),
            opacity=0.9,
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

    map_cfg = dict(
        style=estilo,
        center=dict(lat=center_lat, lon=center_lon),
        zoom=zoom,
    )
    if mapbox_token and map_layout_key == "mapbox":
        map_cfg["accesstoken"] = mapbox_token

    layout_kwargs = {
        map_layout_key: map_cfg,
        "paper_bgcolor": FONDO,
        "font": dict(color=TEXTO),
        "margin": dict(l=0, r=0, t=38, b=0),
        "height": 580,
        "modebar": dict(
            orientation="h",
            bgcolor="rgba(26, 31, 46, 0.85)",
            color="#94A3B8",
            activecolor="#2DD4BF",
        ),
    }
    fig.update_layout(**layout_kwargs)
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

# ─── KPIs de la canasta básica ─────────────────────────────────────────────────────

def barra_horizontal(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """Barra horizontal genérica ordenada descendente.
    df: DataFrame con al menos las columnas `x_col` (valor numérico) y `y_col` (categoría).
    """
    df = df.sort_values(x_col, ascending=True)  # Ascendente para que la barra más alta quede arriba
    fig = go.Figure(go.Bar(
        x=df[x_col],
        y=df[y_col],
        orientation="h",
        marker_color=TEAL,
        text=df[x_col].apply(lambda v: f"{v:,}" if isinstance(v, (int, float)) else str(v)),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df[y_col].tolist())
    return fig

def barra_rango_precio(df: pd.DataFrame, title: str) -> go.Figure:
    """Muestra rango de precios (mín‑máx) por producto usando barras `base` + `width`."""
    df = df.sort_values("precio_minimo", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["producto"],
        x=df["precio_maximo"] - df["precio_minimo"],
        base=df["precio_minimo"],
        orientation="h",
        marker_color=AMBER,
        hovertemplate="%{y}<br>Min: %{base}<br>Max: %{x + base}<extra></extra>",
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df["producto"].tolist())
    return fig

def heatmap_variacion(df: pd.DataFrame, title: str) -> go.Figure:
    """Heatmap de variación porcentual mensual (producto x periodo)."""
    pivot = df.pivot(index="producto", columns="periodo", values="variacion_pct")
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, TEAL], [0.5, "#606060"], [1, AMBER]],
        colorbar=dict(title="% variación"),
    ))
    _aplicar_tema(fig, title)
    fig.update_xaxes(tickangle=-45)
    return fig

def barras_variacion_acumulada(df: pd.DataFrame, title: str) -> go.Figure:
    """Barras divergentes: delta_pct positivo en ámbar, negativo en verde azulado.
    También muestra el delta en pesos como texto.
    """
    colors = [AMBER if v >= 0 else TEAL for v in df["delta_pct"]]
    fig = go.Figure(go.Bar(
        y=df["producto"],
        x=df["delta_pct"],
        orientation="h",
        marker_color=colors,
        text=df["delta_valor"].apply(lambda v: f"{v:,.2f}"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df["producto"].tolist())
    return fig

def barras_top_productos(df: pd.DataFrame, value_col: str, title: str) -> go.Figure:
    """Barras horizontales para top‑N (usada para productos caros, alza, estabilidad)."""
    fig = go.Figure(go.Bar(
        y=df["producto"],
        x=df[value_col],
        orientation="h",
        marker_color=AMBER if "pct" in value_col.lower() else TEAL,
        text=df[value_col].apply(lambda v: f"{v:.2f}%" if isinstance(v, float) else f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df["producto"].tolist())
    return fig

def barras_costo_cadena(df: pd.DataFrame, title: str) -> go.Figure:
    """Barras de costo promedio de la canasta por cadena (solo cadenas con ≥20 productos)."""
    fig = go.Figure(go.Bar(
        y=df["cadena_comercial"],
        x=df["costo_promedio"],
        orientation="h",
        marker_color=TEAL,
        text=df["productos_cubiertos"].apply(lambda v: f"{v} prod"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df["cadena_comercial"].tolist())
    return fig

def barras_diferencia_cadenas(df: pd.DataFrame, title: str) -> go.Figure:
    """Barras que muestran la variación porcentual entre la cadena más cara y la más barata por producto."""
    fig = go.Figure(go.Bar(
        y=df["producto"],
        x=df["variacion_pct"],
        orientation="h",
        marker_color=AMBER,
        hovertemplate=(
            "Producto: %{y}<br>Más cara: %{customdata[0]} (${customdata[1]:,.2f})<br>Más barata: %{customdata[2]} (${customdata[3]:,.2f})<extra></extra>"
        ),
        customdata=df[["cadena_mas_cara", "max_precio", "cadena_mas_barata", "min_precio"]].values,
        text=df["variacion_pct"].apply(lambda v: f"{v:.2f}%"),
        textposition="outside",
        textfont=dict(color=TEXTO, size=11),
    ))
    _aplicar_tema(fig, title)
    fig.update_yaxes(categoryorder="array", categoryarray=df["producto"].tolist())
    return fig

# Fin de sección KPIs
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
