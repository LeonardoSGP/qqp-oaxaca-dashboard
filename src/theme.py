"""
src/theme.py
─────────────────────────────────────────────────────────────────────────────
Sistema de diseño Glassmorphism centralizado basado en `.agents/skills/glassmorphism/SKILL.md`
y `.agents/skills/glassmorphism/references/tokens.css`.
Implementa:
1. Transparencia (`rgba` alpha 0.06–0.40) sobre fondo ambiental multicapa
2. Desenfoque (`backdrop-filter: blur(18px)` + `-webkit-backdrop-filter`)
3. Bordes translúcidos (`1px solid rgba(255, 255, 255, 0.18)`)
4. Sombras multicapa suaves (`box-shadow`)
5. Navegación superior sticky (`.glass-nav` en `header[data-testid="stHeader"]`)
6. Tarjetas homologadas al tamaño de referencia del cuadro con más texto (`168px` + flex stretch)
7. Compatibilidad (`@supports`) y accesibilidad (`prefers-reduced-transparency`, `prefers-contrast`)
"""

import streamlit as st

_GLASS_CSS = """
:root {
    --glass-bg-light: rgba(255, 255, 255, 0.07);
    --glass-bg: rgba(26, 31, 46, 0.38);
    --glass-bg-hover: rgba(38, 46, 68, 0.52);
    --glass-bg-heavy: rgba(14, 17, 23, 0.75);
    --glass-blur-light: blur(10px);
    --glass-blur: blur(18px) saturate(160%);
    --glass-blur-strong: blur(28px) saturate(180%);
    --glass-border: 1px solid rgba(255, 255, 255, 0.18);
    --glass-border-hover: 1px solid rgba(45, 212, 191, 0.48);
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 1px 0 0 rgba(255, 255, 255, 0.12);
    --glass-shadow-elevated: 0 14px 42px 0 rgba(0, 0, 0, 0.50), inset 0 1px 0 0 rgba(255, 255, 255, 0.18);
    --glass-radius: 14px;
    --glass-radius-lg: 18px;
    --card-ref-height: 168px;
    --glass-text: #F8FAFC;
    --glass-text-muted: #CBD5E1;
    --glass-text-sub: #94A3B8;
    --glass-teal: #2DD4BF;
    --glass-amber: #F59E0B;
    --glass-green: #34D399;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
    backgroundColor: #0B0F17;
    background:
        radial-gradient(circle at 12% 18%, rgba(45, 212, 191, 0.15) 0%, transparent 38%),
        radial-gradient(circle at 88% 14%, rgba(56, 189, 248, 0.12) 0%, transparent 36%),
        radial-gradient(circle at 75% 82%, rgba(245, 158, 11, 0.10) 0%, transparent 40%),
        linear-gradient(160deg, #090D14 0%, #0E131F 50%, #111827 100%) !important;
    background-attachment: fixed !important;
    color: var(--glass-text) !important;
}
.block-container {
    max-width: 1320px !important;
    padding-top: 3.6rem !important;
    padding-bottom: 3.5rem !important;
}
/* ─── Navbar superior Glassmorphism (.glass-nav) ─── */
header[data-testid="stHeader"], .glass-nav {
    background: rgba(14, 17, 23, 0.88) !important;
    border-bottom: var(--glass-border) !important;
    box-shadow: var(--glass-shadow) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 100 !important;
}
@supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
    header[data-testid="stHeader"], .glass-nav {
        background: var(--glass-bg-heavy) !important;
        backdrop-filter: var(--glass-blur-strong) !important;
        -webkit-backdrop-filter: var(--glass-blur-strong) !important;
    }
}
header[data-testid="stHeader"] a,
header[data-testid="stHeader"] button,
[data-testid="stTopNavLink"] {
    border-radius: 10px !important;
    color: var(--glass-text-muted) !important;
    font-weight: 500 !important;
    transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease !important;
}
[data-testid="stTopNavLink"]:hover,
header[data-testid="stHeader"] a:hover {
    background: var(--glass-bg-light) !important;
    color: var(--glass-text) !important;
}
[data-testid="stTopNavLink"][aria-current="page"] {
    background: rgba(45, 212, 191, 0.16) !important;
    color: var(--glass-teal) !important;
    border: 1px solid rgba(45, 212, 191, 0.38) !important;
    box-shadow: 0 4px 16px rgba(45, 212, 191, 0.15) !important;
}
/* ─── Barra superior de estado Glassmorphism ─── */
.glass-topbar {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: var(--glass-border);
    border-radius: var(--glass-radius);
    box-shadow: var(--glass-shadow);
    padding: 0.75rem 1.25rem;
    margin-bottom: 1.4rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
}
.glass-topbar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.92rem;
    color: var(--glass-text-muted);
}
.glass-topbar-brand strong {
    color: var(--glass-text);
    font-size: 1rem;
}
.glass-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.32rem 0.85rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(52, 211, 153, 0.14);
    border: 1px solid rgba(52, 211, 153, 0.38);
    color: var(--glass-green);
}
.glass-status-pill.err {
    background: rgba(248, 113, 113, 0.14);
    border: 1px solid rgba(248, 113, 113, 0.38);
    color: #F87171;
}
/* ─── Sidebar Glassmorphism (para filtros de vistas) ─── */
[data-testid="stSidebar"] {
    background: var(--glass-bg-heavy) !important;
    backdrop-filter: var(--glass-blur-strong) !important;
    -webkit-backdrop-filter: var(--glass-blur-strong) !important;
    border-right: var(--glass-border) !important;
    box-shadow: var(--glass-shadow) !important;
}
/* ─── Estiramiento automático de columnas para igualar al cuadro con más texto ─── */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
[data-testid="stColumn"],
[data-testid="stColumn"] > div,
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stColumn"] [data-testid="stVerticalBlock"],
[data-testid="stColumn"] [data-testid="stElementContainer"],
[data-testid="stColumn"] [data-testid="stMarkdown"],
[data-testid="stColumn"] [data-testid="stMarkdownContainer"] {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
}
/* ─── Tarjetas Glassmorphism (.glass-card, .kpi-card, .etl-card) ─── */
.glass-card, .kpi-card, .etl-card {
    box-sizing: border-box !important;
    background: rgba(26, 31, 46, 0.82);
    border: var(--glass-border);
    border-radius: var(--glass-radius);
    box-shadow: var(--glass-shadow);
    padding: 1.35rem 1.45rem;
    height: 100% !important;
    min-height: var(--card-ref-height) !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    flex: 1 1 auto !important;
    transition: transform 0.22s ease, background 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
}
@supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
    .glass-card, .kpi-card, .etl-card {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
    }
}
.glass-card:hover, .kpi-card:hover, .etl-card:hover {
    transform: translateY(-3px);
    background: var(--glass-bg-hover);
    border: var(--glass-border-hover);
    box-shadow: var(--glass-shadow-elevated);
}
.kpi-card {
    text-align: center;
    align-items: center;
}
.kpi-valor {
    font-size: 2rem;
    font-weight: 700;
    color: var(--glass-teal);
    margin: 0;
    line-height: 1.15;
    text-shadow: 0 2px 12px rgba(45, 212, 191, 0.22);
}
.kpi-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--glass-text);
    margin-top: 0.4rem;
    margin-bottom: 0;
    line-height: 1.35;
}
.kpi-sub {
    font-size: 0.78rem;
    color: var(--glass-text-muted);
    margin-top: 0.28rem;
    margin-bottom: 0;
    line-height: 1.35;
}
.etl-card {
    text-align: left;
    justify-content: flex-start !important;
    border-left: 4px solid var(--glass-teal);
}
.etl-card.amber {
    border-left: 4px solid var(--glass-amber);
}
.etl-card.green {
    border-left: 4px solid var(--glass-green);
}
.etl-titulo {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--glass-text);
    margin: 0 0 0.45rem 0;
}
.etl-desc {
    font-size: 0.86rem;
    color: var(--glass-text-muted);
    line-height: 1.5;
    margin: 0;
}
.etl-desc strong {
    color: var(--glass-text);
}
/* ─── Paneles de gráficas, tablas, pestañas y botones Glassmorphism ─── */
[data-testid="stPlotlyChart"] {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: var(--glass-border);
    border-radius: var(--glass-radius);
    box-shadow: var(--glass-shadow);
    padding: 0.5rem;
    overflow: hidden;
}
[data-testid="stDataFrame"] {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur-light);
    -webkit-backdrop-filter: var(--glass-blur-light);
    border: var(--glass-border);
    border-radius: var(--glass-radius);
    box-shadow: var(--glass-shadow);
    overflow: hidden;
}
.glass-btn, .stButton > button {
    background: var(--glass-bg-light) !important;
    backdrop-filter: var(--glass-blur-light) !important;
    -webkit-backdrop-filter: var(--glass-blur-light) !important;
    border: var(--glass-border) !important;
    border-radius: var(--glass-radius) !important;
    color: var(--glass-text) !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
}
.glass-btn:hover, .stButton > button:hover {
    background: var(--glass-bg) !important;
    border: var(--glass-border-hover) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--glass-bg-light);
    backdrop-filter: var(--glass-blur-light);
    -webkit-backdrop-filter: var(--glass-blur-light);
    border: var(--glass-border);
    border-radius: var(--glass-radius);
    padding: 0.3rem;
    gap: 0.4rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: var(--glass-text-muted) !important;
    padding: 0.45rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--glass-bg) !important;
    color: var(--glass-teal) !important;
    border: 1px solid rgba(45, 212, 191, 0.35) !important;
    box-shadow: var(--glass-shadow) !important;
}
.badge-ok  { color: var(--glass-green); font-weight: 700; }
.badge-warn{ color: var(--glass-amber); font-weight: 700; }
.badge-err { color: #F87171; font-weight: 700; }
.separador {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.14);
    margin: 1.5rem 0;
}
/* ─── Accesibilidad: prefers-reduced-transparency y prefers-contrast ─── */
@media (prefers-reduced-transparency: reduce) {
    header[data-testid="stHeader"], .glass-nav, .glass-topbar,
    .glass-card, .kpi-card, .etl-card, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {
        background: rgba(22, 27, 40, 0.95) !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
}
@media (prefers-contrast: more) {
    .glass-card, .kpi-card, .etl-card, .glass-topbar, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {
        background: rgba(15, 20, 30, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.45) !important;
    }
}
"""

_COMPACT_GLASS_CSS = "\n".join(line.strip() for line in _GLASS_CSS.splitlines() if line.strip())


def apply_glassmorphism() -> None:
    """Inyecta las hojas de estilo del sistema Glassmorphism sin saltos vacíos."""
    st.markdown(f"<style>{_COMPACT_GLASS_CSS}</style>", unsafe_allow_html=True)


def render_top_status_bar(conectado: bool, msg_conexion: str) -> None:
    """Renderiza una barra superior Glassmorphism con identidad y estado de MySQL."""
    pill_cls = "glass-status-pill" if conectado else "glass-status-pill err"
    pill_txt = f"● Conectado a MySQL · {msg_conexion}" if conectado else "● Sin conexión a MySQL"
    html = (
        f'<div class="glass-topbar">'
        f'<div class="glass-topbar-brand">'
        f'<strong>QQP Oaxaca · Dashboard</strong>'
        f'<span>|</span>'
        f'<span>Quién es Quién en los Precios · TecNM Campus Oaxaca · 2026</span>'
        f'</div>'
        f'<div class="{pill_cls}">{pill_txt}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
