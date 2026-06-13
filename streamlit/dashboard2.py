import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import time

# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Global Sales Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS GLOBAL — IDENTIDAD VISUAL
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── RESET & BASE ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #090910;
    color: #E8E8F0;
}
.stApp { background: #090910; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0F0F1A !important;
    border-right: 1px solid #1E1E32;
}
[data-testid="stSidebar"] * { color: #B0B0C8 !important; }
[data-testid="stSidebar"] .stRadio > label { 
    font-size: 11px !important; 
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #5A5A7A !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 11px !important;
    color: #5A5A7A !important;
}

/* ── RADIO BUTTONS CUSTOM ── */
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent !important;
    border: 1px solid #1E1E32 !important;
    border-radius: 6px !important;
    padding: 10px 14px !important;
    margin: 3px 0 !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
    display: block !important;
    font-size: 12px !important;
    color: #8888A8 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    border-color: #00D4FF44 !important;
    background: #00D4FF08 !important;
    color: #00D4FF !important;
}

/* ── MAIN HEADER ── */
.main-header {
    background: linear-gradient(135deg, #0F0F1A 0%, #12122A 50%, #0A1020 100%);
    border: 1px solid #1E1E38;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00D4FF, #00FF88, #00D4FF, transparent);
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, #00D4FF11, transparent 70%);
    border-radius: 50%;
}
.header-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.25em;
    color: #00D4FF;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.header-title {
    font-size: 28px;
    font-weight: 800;
    color: #F0F0FF;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 6px;
}
.header-subtitle {
    font-size: 13px;
    color: #6060808;
    color: rgb(100, 100, 140);
    font-weight: 400;
}

/* ── KPI CARDS ── */
.kpi-card {
    background: #0F0F1A;
    border: 1px solid #1E1E32;
    border-radius: 10px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 10px 10px;
}
.kpi-card.blue::after   { background: linear-gradient(90deg, #00D4FF, #0066FF); }
.kpi-card.green::after  { background: linear-gradient(90deg, #00FF88, #00CC66); }
.kpi-card.purple::after { background: linear-gradient(90deg, #AA44FF, #7700CC); }
.kpi-card.orange::after { background: linear-gradient(90deg, #FF8800, #FF4400); }
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #50507A;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-value.blue   { color: #00D4FF; }
.kpi-value.green  { color: #00FF88; }
.kpi-value.purple { color: #BB66FF; }
.kpi-value.orange { color: #FF9922; }
.kpi-delta {
    font-size: 11px;
    color: #50507A;
    font-weight: 500;
}
.kpi-delta .up { color: #00FF88; }
.kpi-delta .down { color: #FF4757; }

/* ── SECTION HEADERS ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 8px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #1A1A2C;
}
.section-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00D4FF;
    box-shadow: 0 0 8px #00D4FF;
    flex-shrink: 0;
}
.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #C0C0E0;
    text-transform: uppercase;
}
.section-sub {
    font-size: 11px;
    color: #40405A;
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
}

/* ── CHART CONTAINER ── */
.chart-panel {
    background: #0C0C18;
    border: 1px solid #181828;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ── DATA TABLE ── */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.data-table th {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #404060;
    padding: 8px 12px;
    border-bottom: 1px solid #181828;
    text-align: left;
}
.data-table td {
    padding: 9px 12px;
    border-bottom: 1px solid #0E0E1C;
    color: #A0A0C0;
}
.data-table tr:hover td { background: #0F0F20; color: #E0E0FF; }
.rank-badge {
    display: inline-block;
    background: #00D4FF15;
    color: #00D4FF;
    border-radius: 4px;
    padding: 2px 7px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
}

/* ── INSIGHT CALLOUT ── */
.insight-box {
    background: linear-gradient(135deg, #001A20, #000D18);
    border: 1px solid #00D4FF22;
    border-left: 3px solid #00D4FF;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0;
}
.insight-box p {
    font-size: 12px;
    color: #80AAC0;
    margin: 0;
    line-height: 1.6;
}
.insight-box strong { color: #00D4FF; }

/* ── STATUS BAR ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    background: #0A0A14;
    border: 1px solid #141424;
    border-radius: 8px;
    padding: 10px 18px;
    margin-bottom: 20px;
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00FF88;
    box-shadow: 0 0 6px #00FF88;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.status-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #404060;
    letter-spacing: 0.1em;
}
.status-text span { color: #00FF88; }

/* ── SIDEBAR LOGO/BRAND ── */
.sidebar-brand {
    text-align: center;
    padding: 20px 0;
    margin-bottom: 12px;
    border-bottom: 1px solid #1A1A2A;
}
.sidebar-brand-icon {
    font-size: 28px;
    margin-bottom: 6px;
}
.sidebar-brand-name {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #00D4FF !important;
}
.sidebar-brand-version {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #303050 !important;
    letter-spacing: 0.15em;
}

/* ── HIDE DEFAULT STREAMLIT ELEMENTS ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 24px !important; padding-bottom: 40px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #090910; }
::-webkit-scrollbar-thumb { background: #1E1E32; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00D4FF44; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY THEME — DARK INDUSTRIAL
# ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#7070A0", size=11),
    margin=dict(l=12, r=12, t=28, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11, color="#8888AA"),
        borderwidth=0,
    ),
    xaxis=dict(
        gridcolor="#12121F",
        linecolor="#1A1A2C",
        tickfont=dict(size=10, color="#505070", family="JetBrains Mono"),
        showgrid=True,
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#12121F",
        linecolor="#1A1A2C",
        tickfont=dict(size=10, color="#505070", family="JetBrains Mono"),
        showgrid=True,
        zeroline=False,
    ),
)
COLOR_SEQ  = ["#00D4FF", "#00FF88", "#AA44FF", "#FF8800", "#FF4757", "#00B8AA", "#FFD700"]
COLOR_MAIN = "#00D4FF"
COLOR_AUX  = "#00FF88"

# ──────────────────────────────────────────────
# DATOS — CARGA Y GENERACIÓN DEMO
# ──────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

def load_csv(filename):
    path = os.path.join(PROCESSED_PATH, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def generate_demo_data():
    """Genera datos demo realistas cuando no hay archivos reales."""
    rng = np.random.default_rng(42)
    np.random.seed(42)

    # Mensual (2021-2024)
    dates = pd.date_range("2021-01", periods=48, freq="MS")
    base   = 1_200_000
    trend  = np.linspace(0, 800_000, 48)
    seas   = np.array([np.sin(i * np.pi / 6) * 200_000 for i in range(48)])
    rev    = (base + trend + seas + rng.normal(0, 50_000, 48)).clip(800_000)
    vol    = (rev / rng.uniform(45, 65, 48)).astype(int)
    df_month = pd.DataFrame({
        "date": dates.strftime("%Y-%m"),
        "total_sales_revenue": rev.round(0),
        "total_sales_volume":  vol,
        "unit_revenue": (rev / vol).round(2),
    })

    # Anual
    df_year = df_month.copy()
    df_year["year"] = df_month["date"].str[:4].astype(int)
    df_year = df_year.groupby("year", as_index=False).agg(
        total_sales_revenue=("total_sales_revenue", "sum"),
        total_sales_volume=("total_sales_volume", "sum"),
        unit_revenue=("unit_revenue", "mean"),
    )

    # Pareto categorías
    cats  = ["Electronics", "Apparel", "Home & Garden", "Sports", "Beauty", "Toys", "Books", "Automotive"]
    sales = [3_200_000, 2_100_000, 1_500_000, 980_000, 720_000, 450_000, 280_000, 190_000]
    cum   = np.cumsum(sales) / sum(sales) * 100
    df_cat_pareto = pd.DataFrame({
        "product_category": cats,
        "total_revenue": sales,
        "cumulative_percentage": cum.round(1),
    })

    # Por país
    countries = ["United States", "Germany", "United Kingdom", "France", "Japan",
                 "Australia", "Canada", "Brazil", "India", "Mexico"]
    rev_c = [4_200_000, 1_800_000, 1_500_000, 1_100_000, 950_000,
             780_000, 720_000, 450_000, 380_000, 290_000]
    df_country = pd.DataFrame({"country": countries, "total_sales_revenue": rev_c,
                                "total_sales_volume": [int(r/55) for r in rev_c]})

    # Por ciudad
    cities = ["New York", "Los Angeles", "Berlin", "London", "Paris",
              "Tokyo", "Sydney", "Toronto", "São Paulo", "Madrid",
              "Chicago", "Munich", "Manchester", "Lyon", "Osaka"]
    rev_ci = [1_200_000, 980_000, 870_000, 820_000, 760_000,
              690_000, 610_000, 580_000, 450_000, 400_000,
              390_000, 370_000, 340_000, 280_000, 260_000]
    df_city = pd.DataFrame({"city": cities, "total_sales_revenue": rev_ci,
                             "total_sales_volume": [int(r/58) for r in rev_ci]})

    # Por día de semana
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    rev_d = [820_000, 780_000, 850_000, 910_000, 1_050_000, 980_000, 720_000]
    vol_d = [int(r/54) for r in rev_d]
    df_weekday = pd.DataFrame({
        "weekday_name": days,
        "weekday_number": range(1, 8),
        "total_sales_revenue": rev_d,
        "total_sales_volume":  vol_d,
        "unit_revenue": [r/v for r, v in zip(rev_d, vol_d)],
    })

    return df_month, df_year, df_cat_pareto, df_country, df_weekday, df_city

# ── Carga real o demo ──
df_month     = load_csv("ft_transactions_per_month.csv")
df_year      = load_csv("ft_transactions_per_year.csv")
df_cat_pareto= load_csv("ft_productcategory_pareto.csv")
df_country   = load_csv("ft_transactions_per_country.csv")
df_weekday   = load_csv("ft_transactions_per_weekday.csv")
df_city      = load_csv("ft_transactions_per_city.csv")

DEMO_MODE = any(df is None for df in [df_month, df_year, df_cat_pareto, df_country, df_weekday, df_city])
if DEMO_MODE:
    df_month, df_year, df_cat_pareto, df_country, df_weekday, df_city = generate_demo_data()

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">⚡</div>
        <div class="sidebar-brand-name">SALES INTEL</div>
        <div class="sidebar-brand-version">v2.0 · GLOBAL OPS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#303050;margin-bottom:8px;">MÓDULOS</p>', unsafe_allow_html=True)
    
    view = st.radio(
        "",
        options=[
            "⚡  Resumen Ejecutivo",
            "📦  Productos & Pareto",
            "🌍  Expansión Geográfica",
            "📅  Comportamiento Semanal",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    
    if DEMO_MODE:
        st.markdown("""
        <div style="background:#FF880011;border:1px solid #FF880033;border-radius:6px;padding:10px 12px;">
            <p style="font-size:10px;color:#FF8800;margin:0;font-family:'JetBrains Mono',monospace;">
            ⚠ DEMO MODE<br>
            <span style="color:#505050;">CSVs no encontrados.<br>Usando datos sintéticos.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#00FF8808;border:1px solid #00FF8822;border-radius:6px;padding:10px 12px;">
            <p style="font-size:10px;color:#00FF88;margin:0;font-family:'JetBrains Mono',monospace;">
            ✓ DATA LOADED<br>
            <span style="color:#505050;">Pipeline OK · Estrella Schema</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <br>
    <div style="padding-top:20px;border-top:1px solid #141424;">
        <p style="font-size:9px;color:#252535;font-family:'JetBrains Mono',monospace;line-height:1.8;">
        DIMS: dim_location · dim_product<br>
        FACTS: sales_clean · 6x ft_*<br>
        SCHEMA: Star · Normalized
        </p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# STATUS BAR
# ──────────────────────────────────────────────
total_rev = df_year["total_sales_revenue"].sum()
total_vol = df_year["total_sales_volume"].sum()
n_markets = len(df_country)

st.markdown(f"""
<div class="status-bar">
    <div class="status-dot"></div>
    <span class="status-text">SISTEMA <span>ONLINE</span></span>
    <span class="status-text" style="margin-left:8px;">REVENUE TOTAL <span>${total_rev/1e6:.2f}M</span></span>
    <span class="status-text">VOLUMEN <span>{total_vol:,}</span> UNIDADES</span>
    <span class="status-text">MERCADOS <span>{n_markets}</span> PAÍSES</span>
    <span class="status-text" style="margin-left:auto;">{"MODO DEMO" if DEMO_MODE else "DATOS REALES"}</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# VISTA 1 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
if "Resumen" in view:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ GLOBAL SALES INTELLIGENCE</div>
        <div class="header-title">Resumen Ejecutivo</div>
        <div class="header-subtitle">Rendimiento financiero histórico · Visión consolidada de ingresos y volumen</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS ──
    avg_unit = total_rev / total_vol if total_vol > 0 else 0
    yoy_rev  = (df_year.iloc[-1]["total_sales_revenue"] / df_year.iloc[-2]["total_sales_revenue"] - 1) * 100 if len(df_year) >= 2 else 0
    yoy_vol  = (df_year.iloc[-1]["total_sales_volume"]  / df_year.iloc[-2]["total_sales_volume"]  - 1) * 100 if len(df_year) >= 2 else 0

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "INGRESOS TOTALES", f"${total_rev/1e6:.2f}M", f"YoY {yoy_rev:+.1f}%", "blue"),
        (c2, "VOLUMEN DE VENTAS", f"{total_vol/1e3:.1f}K", f"YoY {yoy_vol:+.1f}% unidades", "green"),
        (c3, "TICKET UNITARIO PROM.", f"${avg_unit:.2f}", "Promedio histórico", "purple"),
        (c4, "MERCADOS ACTIVOS", str(n_markets), "Países con ventas activas", "orange"),
    ]
    for col, label, val, delta, color in cards:
        sign = "up" if "+" in delta else ("down" if "-" in delta and "%" in delta else "")
        delta_html = f'<span class="{sign}">{delta}</span>' if sign else f'<span>{delta}</span>'
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color}">{val}</div>
                <div class="kpi-delta">{delta_html}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── EVOLUCIÓN MENSUAL ──
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot"></div>
            <div class="section-title">Evolución mensual de ingresos</div>
            <div class="section-sub">48 meses</div>
        </div>
        """, unsafe_allow_html=True)

        df_m = df_month.copy()
        df_m["date"] = pd.to_datetime(df_m["date"])
        df_m = df_m.sort_values("date")

        fig_trend = go.Figure()
        # Área de fondo suave
        fig_trend.add_trace(go.Scatter(
            x=df_m["date"], y=df_m["total_sales_revenue"],
            fill="tozeroy",
            fillcolor="rgba(0, 212, 255, 0.06)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))
        # Línea principal
        fig_trend.add_trace(go.Scatter(
            x=df_m["date"], y=df_m["total_sales_revenue"],
            mode="lines",
            line=dict(color="#00D4FF", width=2.5),
            name="Ingresos",
            hovertemplate="<b>%{x|%b %Y}</b><br>$%{y:,.0f}<extra></extra>",
        ))
        # Media móvil
        df_m["ma3"] = df_m["total_sales_revenue"].rolling(3).mean()
        fig_trend.add_trace(go.Scatter(
            x=df_m["date"], y=df_m["ma3"],
            mode="lines",
            line=dict(color="#00FF88", width=1.5, dash="dot"),
            name="MA 3M",
            hovertemplate="MA 3M: $%{y:,.0f}<extra></extra>",
        ))
        fig_trend.update_layout(**PLOT_LAYOUT, height=280,
            legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_r:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot" style="background:#00FF88;box-shadow:0 0 8px #00FF88;"></div>
            <div class="section-title">Ingresos por año</div>
        </div>
        """, unsafe_allow_html=True)

        fig_year = go.Figure(go.Bar(
            x=df_year["year"].astype(str),
            y=df_year["total_sales_revenue"],
            marker=dict(
                color=df_year["total_sales_revenue"],
                colorscale=[[0, "#003344"], [0.5, "#006699"], [1, "#00D4FF"]],
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=[f"${v/1e6:.2f}M" for v in df_year["total_sales_revenue"]],
            textposition="outside",
            textfont=dict(size=11, color="#00D4FF", family="JetBrains Mono"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
            width=0.6,
        ))
        fig_year.update_layout(**PLOT_LAYOUT, height=280,
            xaxis=dict(**PLOT_LAYOUT["xaxis"], type="category"),
            yaxis=dict(**PLOT_LAYOUT["yaxis"], showticklabels=False, showgrid=False),
        )
        st.plotly_chart(fig_year, use_container_width=True)

    # ── VOLUMEN vs TICKET ──
    st.markdown("""
    <div class="section-header">
        <div class="section-dot" style="background:#AA44FF;box-shadow:0 0 8px #AA44FF;"></div>
        <div class="section-title">Volumen vs ticket promedio</div>
        <div class="section-sub">Correlación mensual</div>
    </div>
    """, unsafe_allow_html=True)

    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(
        x=df_m["date"], y=df_m["total_sales_volume"],
        name="Volumen",
        marker_color="rgba(170, 68, 255, 0.5)",
        yaxis="y",
        hovertemplate="Volumen: %{y:,}<extra></extra>",
    ))
    fig_dual.add_trace(go.Scatter(
        x=df_m["date"], y=df_m["unit_revenue"],
        name="Ticket Prom.",
        mode="lines+markers",
        line=dict(color="#FF8800", width=2),
        marker=dict(size=4, color="#FF8800"),
        yaxis="y2",
        hovertemplate="Ticket: $%{y:.2f}<extra></extra>",
    ))
    fig_dual.update_layout(
        **PLOT_LAYOUT, height=220,
        yaxis2=dict(overlaying="y", side="right",
                    tickfont=dict(size=10, color="#505070", family="JetBrains Mono"),
                    gridcolor="rgba(0,0,0,0)", zeroline=False),
        legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"),
        barmode="overlay",
    )
    st.plotly_chart(fig_dual, use_container_width=True)


# ══════════════════════════════════════════════
# VISTA 2 — PRODUCTOS & PARETO
# ══════════════════════════════════════════════
elif "Productos" in view:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ CATÁLOGO & RENDIMIENTO</div>
        <div class="header-title">Análisis de Productos</div>
        <div class="header-subtitle">Regla 80/20 · Identificación de categorías que traccionan el negocio</div>
    </div>
    """, unsafe_allow_html=True)

    # ── PARETO ──
    df_p = df_cat_pareto.copy().sort_values("total_revenue", ascending=False)
    
    col_kp1, col_kp2, col_kp3 = st.columns(3)
    top1 = df_p.iloc[0]
    cats_to_80 = (df_p["cumulative_percentage"] <= 80).sum() + 1
    top3_share = df_p.head(3)["total_revenue"].sum() / df_p["total_revenue"].sum() * 100

    for col, label, val, color in [
        (col_kp1, "CAT. LÍDER", top1["product_category"], "blue"),
        (col_kp2, "CATS PARA 80% REV.", str(cats_to_80), "green"),
        (col_kp3, "SHARE TOP 3", f"{top3_share:.1f}%", "purple"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color}" style="font-size:22px;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <div class="section-dot"></div>
        <div class="section-title">Diagrama de Pareto — Ingresos por categoría</div>
        <div class="section-sub">Regla 80/20</div>
    </div>
    """, unsafe_allow_html=True)

    fig_pareto = go.Figure()
    
    # Barras con gradiente de color
    bar_colors = [
        f"rgba(0, 212, 255, {max(0.35, 1 - i*0.11)})" 
        for i in range(len(df_p))
    ]
    fig_pareto.add_trace(go.Bar(
        x=df_p["product_category"],
        y=df_p["total_revenue"],
        name="Ingresos",
        marker=dict(color=bar_colors, line=dict(width=0)),
        yaxis="y",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    # Línea acumulada
    fig_pareto.add_trace(go.Scatter(
        x=df_p["product_category"],
        y=df_p["cumulative_percentage"],
        name="% Acumulado",
        mode="lines+markers",
        line=dict(color="#00FF88", width=2.5),
        marker=dict(size=7, color="#00FF88", symbol="diamond",
                    line=dict(color="#090910", width=1.5)),
        yaxis="y2",
        hovertemplate="%{y:.1f}% acumulado<extra></extra>",
    ))
    # Línea 80%
    fig_pareto.add_hline(
        y=80, line_dash="dot", line_color="#FF475744",
        annotation_text="  Umbral 80%", annotation_font_color="#FF4757",
        annotation_font_size=10, yref="y2",
    )

    fig_pareto.update_layout(
        **PLOT_LAYOUT, height=380,
        yaxis=dict(**PLOT_LAYOUT["yaxis"], title="Ingresos (USD)"),
        yaxis2=dict(
            title="% Acumulado", overlaying="y", side="right",
            range=[0, 110], ticksuffix="%",
            tickfont=dict(size=10, color="#505070", family="JetBrains Mono"),
            gridcolor="rgba(0,0,0,0)", zeroline=False,
        ),
        legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
        bargap=0.25,
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # ── TABLA DETALLE ──
    st.markdown("""
    <div class="section-header">
        <div class="section-dot" style="background:#AA44FF;box-shadow:0 0 8px #AA44FF;"></div>
        <div class="section-title">Detalle por categoría</div>
    </div>
    """, unsafe_allow_html=True)

    rows_html = ""
    for i, row in df_p.reset_index(drop=True).iterrows():
        is_vital = "✓ VITAL" if row["cumulative_percentage"] <= 80 else "TRIVIAL"
        vital_color = "#00FF88" if row["cumulative_percentage"] <= 80 else "#303050"
        rows_html += f"""
        <tr>
            <td><span class="rank-badge">#{i+1:02d}</span></td>
            <td style="color:#C0C0E0;font-weight:500;">{row['product_category']}</td>
            <td style="color:#00D4FF;font-family:'JetBrains Mono',monospace;">${row['total_revenue']:,.0f}</td>
            <td style="font-family:'JetBrains Mono',monospace;">{row['cumulative_percentage']:.1f}%</td>
            <td style="color:{vital_color};font-size:10px;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;">{is_vital}</td>
        </tr>"""

    st.markdown(f"""
    <div class="chart-panel">
    <table class="data-table">
        <thead><tr>
            <th>#</th><th>CATEGORÍA</th><th>INGRESOS</th><th>ACUM.</th><th>PARETO</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <p>📌 <strong>Insight:</strong> Las categorías clasificadas como <strong>VITAL</strong> 
        representan menos del 30% del catálogo pero generan el 80% de los ingresos. 
        Optimizar stock, marketing y márgenes en estas categorías tiene el mayor retorno potencial.</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# VISTA 3 — EXPANSIÓN GEOGRÁFICA
# ══════════════════════════════════════════════
elif "Geográfica" in view:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ PRESENCIA GLOBAL</div>
        <div class="header-title">Expansión Geográfica</div>
        <div class="header-subtitle">Distribución de ingresos por país y ciudad · Oportunidades de mercado</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs GEO ──
    top_country = df_country.nlargest(1, "total_sales_revenue").iloc[0]
    top_city    = df_city.nlargest(1, "total_sales_revenue").iloc[0]
    top3_rev    = df_country.nlargest(3, "total_sales_revenue")["total_sales_revenue"].sum()
    top3_pct    = top3_rev / df_country["total_sales_revenue"].sum() * 100

    cg1, cg2, cg3 = st.columns(3)
    for col, label, val, color in [
        (cg1, "PAÍS LÍDER",    top_country["country"], "blue"),
        (cg2, "CIUDAD LÍDER",  top_city["city"],       "green"),
        (cg3, "CONC. TOP 3 PAÍSES", f"{top3_pct:.1f}%", "purple"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color}" style="font-size:22px;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAPA ──
    st.markdown("""
    <div class="section-header">
        <div class="section-dot"></div>
        <div class="section-title">Mapa de calor de ingresos</div>
        <div class="section-sub">Choropleth global</div>
    </div>
    """, unsafe_allow_html=True)

    fig_map = px.choropleth(
        df_country,
        locations="country", locationmode="country names",
        color="total_sales_revenue",
        hover_name="country",
        hover_data={"total_sales_revenue": ":,.0f"},
        color_continuous_scale=[
            [0,   "#0A0A18"],
            [0.2, "#003344"],
            [0.5, "#006688"],
            [0.8, "#00AACC"],
            [1,   "#00D4FF"],
        ],
        labels={"total_sales_revenue": "Ingresos"},
    )
    fig_map.update_layout(
        **PLOT_LAYOUT,
        height=380,
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            landcolor="#12121F",
            oceancolor="#0A0A14",
            showocean=True,
            lakecolor="#0A0A14",
            showframe=False,
            coastlinecolor="#1E1E30",
            projection_type="natural earth",
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color="#505070", size=9, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)",
            outlinewidth=0,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── TOP PAÍSES + TOP CIUDADES ──
    col_countries, col_cities = st.columns([1, 1])

    with col_countries:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot" style="background:#00FF88;box-shadow:0 0 8px #00FF88;"></div>
            <div class="section-title">Top 10 países</div>
        </div>
        """, unsafe_allow_html=True)

        top10c = df_country.nlargest(10, "total_sales_revenue").sort_values("total_sales_revenue")
        max_rev = top10c["total_sales_revenue"].max()

        fig_countries = go.Figure(go.Bar(
            x=top10c["total_sales_revenue"],
            y=top10c["country"],
            orientation="h",
            marker=dict(
                color=top10c["total_sales_revenue"],
                colorscale=[[0, "#003344"], [1, "#00D4FF"]],
                line=dict(width=0),
            ),
            text=[f"${v/1e6:.2f}M" for v in top10c["total_sales_revenue"]],
            textposition="outside",
            textfont=dict(size=9, color="#606080", family="JetBrains Mono"),
            hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>",
        ))
        fig_countries.update_layout(
            **PLOT_LAYOUT, height=340,
            xaxis=dict(**PLOT_LAYOUT["xaxis"], showticklabels=False, showgrid=False),
            yaxis=dict(**PLOT_LAYOUT["yaxis"], tickfont=dict(size=10, color="#8888AA")),
        )
        st.plotly_chart(fig_countries, use_container_width=True)

    with col_cities:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot" style="background:#AA44FF;box-shadow:0 0 8px #AA44FF;"></div>
            <div class="section-title">Top 10 ciudades</div>
        </div>
        """, unsafe_allow_html=True)

        top10ci = df_city.nlargest(10, "total_sales_revenue").sort_values("total_sales_revenue")
        fig_cities = go.Figure(go.Bar(
            x=top10ci["total_sales_revenue"],
            y=top10ci["city"],
            orientation="h",
            marker=dict(
                color=top10ci["total_sales_revenue"],
                colorscale=[[0, "#1A0033"], [1, "#AA44FF"]],
                line=dict(width=0),
            ),
            text=[f"${v/1e3:.0f}K" for v in top10ci["total_sales_revenue"]],
            textposition="outside",
            textfont=dict(size=9, color="#606080", family="JetBrains Mono"),
            hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>",
        ))
        fig_cities.update_layout(
            **PLOT_LAYOUT, height=340,
            xaxis=dict(**PLOT_LAYOUT["xaxis"], showticklabels=False, showgrid=False),
            yaxis=dict(**PLOT_LAYOUT["yaxis"], tickfont=dict(size=10, color="#8888AA")),
        )
        st.plotly_chart(fig_cities, use_container_width=True)


# ══════════════════════════════════════════════
# VISTA 4 — COMPORTAMIENTO SEMANAL
# ══════════════════════════════════════════════
elif "Semanal" in view:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ PATRONES TEMPORALES</div>
        <div class="header-title">Comportamiento Semanal</div>
        <div class="header-subtitle">Distribución de ingresos y volumen por día de la semana · Patrones de compra</div>
    </div>
    """, unsafe_allow_html=True)

    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    df_w = df_weekday.copy()
    df_w["weekday_name"] = pd.Categorical(df_w["weekday_name"], categories=orden_dias, ordered=True)
    df_w = df_w.sort_values("weekday_name")

    best_day  = df_w.loc[df_w["total_sales_revenue"].idxmax(), "weekday_name"]
    worst_day = df_w.loc[df_w["total_sales_revenue"].idxmin(), "weekday_name"]
    best_ticket = df_w.loc[df_w["unit_revenue"].idxmax(), "weekday_name"]

    cw1, cw2, cw3 = st.columns(3)
    for col, label, val, color in [
        (cw1, "DÍA PICO (INGRESOS)", best_day,   "blue"),
        (cw2, "DÍA PICO (TICKET)",   best_ticket, "green"),
        (cw3, "DÍA MÁS BAJO",        worst_day,  "orange"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color}" style="font-size:24px;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HEATMAP-STYLE POLAR ──
    col_main, col_side = st.columns([3, 2])

    with col_main:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot"></div>
            <div class="section-title">Ingresos por día de la semana</div>
        </div>
        """, unsafe_allow_html=True)

        colors_days = [
            "#00D4FF" if d == best_day else 
            ("rgba(0,212,255,0.25)" if d != worst_day else "#FF475760")
            for d in df_w["weekday_name"]
        ]
        fig_wd = go.Figure(go.Bar(
            x=df_w["weekday_name"],
            y=df_w["total_sales_revenue"],
            marker_color=colors_days,
            marker_line_width=0,
            text=[f"${v/1e3:.0f}K" for v in df_w["total_sales_revenue"]],
            textposition="outside",
            textfont=dict(size=10, family="JetBrains Mono", color="#606080"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
            width=0.65,
        ))
        avg_rev = df_w["total_sales_revenue"].mean()
        fig_wd.add_hline(
            y=avg_rev, line_dash="dot", line_color="#FFFFFF22",
            annotation_text=f"  Promedio ${avg_rev/1e3:.0f}K",
            annotation_font_color="#404060",
            annotation_font_size=9,
        )
        fig_wd.update_layout(**PLOT_LAYOUT, height=300,
            yaxis=dict(**PLOT_LAYOUT["yaxis"], showticklabels=False, showgrid=False))
        st.plotly_chart(fig_wd, use_container_width=True)

    with col_side:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot" style="background:#FF8800;box-shadow:0 0 8px #FF8800;"></div>
            <div class="section-title">Ticket promedio</div>
        </div>
        """, unsafe_allow_html=True)

        fig_ticket = go.Figure(go.Scatter(
            x=df_w["weekday_name"],
            y=df_w["unit_revenue"],
            mode="lines+markers",
            line=dict(color="#FF8800", width=2.5),
            marker=dict(
                size=10, color="#FF8800",
                symbol="circle",
                line=dict(color="#090910", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(255, 136, 0, 0.05)",
            hovertemplate="<b>%{x}</b><br>Ticket: $%{y:.2f}<extra></extra>",
        ))
        fig_ticket.update_layout(**PLOT_LAYOUT, height=300)
        st.plotly_chart(fig_ticket, use_container_width=True)

    # ── VOLUMEN ──
    st.markdown("""
    <div class="section-header">
        <div class="section-dot" style="background:#AA44FF;box-shadow:0 0 8px #AA44FF;"></div>
        <div class="section-title">Volumen de transacciones por día</div>
        <div class="section-sub">Unidades vendidas</div>
    </div>
    """, unsafe_allow_html=True)

    fig_vol_w = go.Figure(go.Bar(
        x=df_w["weekday_name"],
        y=df_w["total_sales_volume"],
        marker=dict(
            color=df_w["total_sales_volume"],
            colorscale=[[0, "#1A0033"], [0.5, "#6622AA"], [1, "#AA44FF"]],
            line=dict(width=0),
        ),
        text=df_w["total_sales_volume"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono", color="#606080"),
        hovertemplate="<b>%{x}</b><br>%{y:,} unidades<extra></extra>",
        width=0.55,
    ))
    fig_vol_w.update_layout(**PLOT_LAYOUT, height=220,
        yaxis=dict(**PLOT_LAYOUT["yaxis"], showticklabels=False, showgrid=False))
    st.plotly_chart(fig_vol_w, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <p>📌 <strong>Insight:</strong> <strong>{best_day}</strong> es el día de mayor ingreso, 
        mientras que el ticket unitario más alto se registra los <strong>{best_ticket}</strong>. 
        Campañas de email o push el <strong>{best_day}</strong> y estrategias de up-sell los 
        <strong>{best_ticket}</strong> podrían maximizar ambas métricas simultáneamente.</p>
    </div>
    """, unsafe_allow_html=True)