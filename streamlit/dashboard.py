import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
import re

# ──────────────────────────────────────────────
# 1. CONFIGURACIÓN Y FORMATO LATINO
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Global Sales Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

def fmt_num(val, is_currency=False, show_sign=False):
    if pd.isna(val): return "0"
    sign = "+" if show_sign and val > 0 else ""
    num_str = f"{int(round(abs(val))):,}".replace(",", ".")
    if val < 0 and not show_sign: num_str = f"-{num_str}"
    elif val < 0 and show_sign: num_str = f"-{num_str}"
    return f"{sign}${num_str}" if is_currency else f"{sign}{num_str}"

def fmt_pct(val):
    if pd.isna(val) or np.isinf(val): return "0%"
    sign = "+" if val > 0 else ""
    return f"{sign}{int(round(val))}%"

def fmt_pct_score(val):
    if pd.isna(val) or np.isinf(val): return "N/A"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:,.1f}%"

meses_es_dict = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}

if "metric" not in st.session_state:
    st.session_state.metric = "Ingresos"

def set_metric(m):
    st.session_state.metric = m

# ──────────────────────────────────────────────
# 2. CSS GLOBAL — ESTÉTICA NATIVA Y LIMPIA
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #090910; color: #F4F4F8; }
.stApp { background: #090910; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background: #0F0F1A !important; border-right: 1px solid #1E1E32; }
[data-testid="stSidebar"] * { color: #D0D0E0 !important; } 
[data-testid="stSidebar"] [role="radiogroup"] div[data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] [role="radiogroup"] label { background: #151525 !important; border: 1px solid #2A2A40 !important; border-radius: 8px !important; padding: 14px 16px !important; margin: 6px 0 !important; transition: all 0.3s !important; cursor: pointer !important; display: flex !important; align-items: center !important; }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-size: 13px !important; color: #C0C0E0 !important; font-weight: 500 !important; margin: 0 !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { border-color: #00D4FF88 !important; background: #00D4FF0A !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: linear-gradient(90deg, #00D4FF15, transparent) !important; border-color: #00D4FF !important; border-left: 4px solid #00D4FF !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: #00D4FF !important; font-weight: 700 !important; }

/* ── HEADER PRINCIPAL ── */
.main-header { background: linear-gradient(135deg, #0F0F1A 0%, #12122A 50%, #0A1020 100%); border: 1px solid #1E1E38; border-radius: 12px; padding: 20px 30px; margin-bottom: 20px; position: relative; overflow: hidden; }
.main-header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00D4FF, #00FF88, #00D4FF, transparent); }
.header-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; letter-spacing: 0.25em; color: #00D4FF; text-transform: uppercase; margin-bottom: 6px; }
.header-title { font-size: 24px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 4px; }
.header-subtitle { font-size: 13px; color: #A0A0C0; font-weight: 400; }

/* ── KPI CARDS COMPACTAS ── */
.kpi-card { background: #0F0F1A; border-radius: 10px; padding: 15px 15px 10px 15px; position: relative; overflow: hidden; border: 1px solid #25253A; transition: all 0.3s; }
.kpi-card::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px; border-radius: 0 0 10px 10px; }
.kpi-card.blue::after   { background: linear-gradient(90deg, #00D4FF, #0066FF); }
.kpi-card.green::after  { background: linear-gradient(90deg, #00FF88, #00CC66); }
.kpi-card.purple::after { background: linear-gradient(90deg, #AA44FF, #7700CC); }
.kpi-card.orange::after { background: linear-gradient(90deg, #FF8800, #FF4400); }
.kpi-card.red::after    { background: linear-gradient(90deg, #FF4757, #CC0000); }

.kpi-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #8888AA; margin-bottom: 4px; text-align: center; }
.kpi-value { font-size: 28px; font-weight: 900; letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 5px; text-align: center; }
.kpi-value.blue   { color: #00D4FF; } .kpi-value.green  { color: #00FF88; } .kpi-value.purple { color: #BB66FF; } .kpi-value.orange { color: #FF9922; } .kpi-value.red    { color: #FF4757; }

.delta-table-mini { width: 100%; margin-top: 4px; border-collapse: collapse; }
.delta-table-mini td { font-size: 10px; padding: 3px 0; border-top: 1px solid #151525; }
.delta-lbl { color: #656585; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; text-align: left; }
.delta-val { font-weight: 600; text-align: right; } .delta-val.up { color: #00FF88; } .delta-val.down { color: #FF4757; } .delta-val.neutro { color: #8888AA; }

/* ── RADIO BUTTON INLINE (Selectores) ── */
[data-testid="stMain"] [data-testid="stRadio"] > div { display: flex; gap: 8px; flex-direction: row; align-items: center; }
[data-testid="stMain"] [data-testid="stRadio"] label { background: #151525 !important; border: 1px solid #2A2A40 !important; border-radius: 6px !important; padding: 6px 14px !important; margin: 0 !important; cursor: pointer !important; transition: all 0.2s; }
[data-testid="stMain"] [data-testid="stRadio"] label p { font-size: 12px !important; color: #A0A0C0 !important; margin: 0 !important;}
[data-testid="stMain"] [data-testid="stRadio"] label:has(input:checked) { background: #00D4FF15 !important; border-color: #00D4FF !important; }
[data-testid="stMain"] [data-testid="stRadio"] label:has(input:checked) p { color: #00D4FF !important; font-weight: 600 !important; }
div[data-testid*="Column"]:nth-of-type(1) div[data-testid="stRadio"] > div { justify-content: flex-start !important; width: 100% !important; }

/* ── SELECTBOXES OSCUROS ── */
.stSelectbox label p { color: #8888AA !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.05em; }
.stSelectbox div[data-baseweb="select"] > div { background-color: #151525 !important; border: 1px solid #2A2A40 !important; border-radius: 8px !important; color: #F4F4F8 !important; }
div[data-baseweb="popover"] > div { background-color: #151525 !important; border: 1px solid #2A2A40 !important; border-radius: 8px !important; }
ul[data-baseweb="menu"] { background-color: #151525 !important; }
ul[data-baseweb="menu"] li { background-color: transparent !important; color: #D0D0E0 !important; transition: background 0.2s; }
ul[data-baseweb="menu"] li:hover, ul[data-baseweb="menu"] li[aria-selected="true"] { background-color: #00D4FF15 !important; color: #00D4FF !important; }

/* ── TABS (Pestañas) ── */
div[data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #25253A; gap: 20px; }
div[data-baseweb="tab"] { background-color: transparent !important; border: none !important; color: #8888AA !important; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; font-size: 12px; padding-bottom: 10px; }
div[aria-selected="true"] { color: #00D4FF !important; border-bottom: 2px solid #00D4FF !important; }

/* ── HEADERS COMUNES ── */
.section-header { display: flex; align-items: center; gap: 10px; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid #1A1A2C; }
.section-dot { width: 6px; height: 6px; border-radius: 50%; background: #00D4FF; box-shadow: 0 0 8px #00D4FF; flex-shrink: 0; }
.section-title { font-size: 14px; font-weight: 700; letter-spacing: 0.05em; color: #E0E0F0; text-transform: uppercase; }

.chart-panel { background: #0C0C18; border: 1px solid #202035; border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase; color: #9090B0; padding: 10px 12px; border-bottom: 1px solid #25253A; text-align: left; }
.data-table td { padding: 12px; border-bottom: 1px solid #1A1A2A; color: #D0D0E0; }
.rank-badge { display: inline-block; background: #00D4FF15; color: #00D4FF; border-radius: 4px; padding: 3px 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 20px !important; padding-bottom: 20px !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 3. GLOBALES: PLOTLY THEME Y COLORES INDUSTRIALES
# ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#A0A0C0", size=11),
    margin=dict(l=10, r=10, t=25, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#D0D0E0"), borderwidth=0),
    xaxis=dict(gridcolor="#1A1A2A", linecolor="#2A2A40", tickfont=dict(size=10, color="#9090B0", family="JetBrains Mono"), showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1A1A2A", linecolor="#2A2A40", tickfont=dict(size=10, color="#9090B0", family="JetBrains Mono"), showgrid=True, zeroline=False),
)

INDUSTRIAL_COLORS = ["#00D4FF", "#00FF88", "#FF4400", "#BB66FF", "#FFCC00", "#FF007F", "#BFFF00", "#00FFFF", "#FF2A2A", "#E0E0F0", "#55AAFF", "#FF88AA", "#AAFFAA"]

# ──────────────────────────────────────────────
# 4. CARGA DE DATOS DESDE EL ETL
# ──────────────────────────────────────────────
PROCESSED_PATH = "/data/processed"

@st.cache_data
def load_csv(filename):
    path = os.path.join(PROCESSED_PATH, filename)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

df_daily       = load_csv("ft_sales_daily.csv")
df_deep_dive   = load_csv("ft_deep_dive.csv")
df_geo_summary = load_csv("ft_geo_summary.csv")
df_scorecard   = load_csv("ft_scorecard.csv")

if not df_daily.empty: df_daily["date"] = pd.to_datetime(df_daily["date"])
if not df_deep_dive.empty: df_deep_dive["date"] = pd.to_datetime(df_deep_dive["date"])

# ──────────────────────────────────────────────
# 5. SIDEBAR (LOGO Y NAVEGACIÓN)
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: -60px; margin-bottom: 20px; text-align: center;">
        <img src="https://img.freepik.com/fotos-premium/mapa-digital-mundo-nodos-lineas-brillantes-que-representan-red-global-computadoras-datos_1187703-14966.jpg?w=1060" style="width: 110px; height: 110px; object-fit: cover; border-radius: 50%; margin-bottom: 15px; box-shadow: 0 0 25px rgba(0, 212, 255, 0.35);">
        <div style="font-size: 22px; font-weight: 900; color: #F4F4F8; letter-spacing: 0.05em; font-family: 'Inter', sans-serif; margin-right: -0.05em;">SALES INTEL</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<p style="font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#8080A0;margin-bottom:8px;text-align:center;">MÓDULOS</p>', unsafe_allow_html=True)
    
    view = st.radio("", options=["⚡  Resumen Ejecutivo", "🔬  Causa Raíz (Deep Dive)", "📦  Análisis Pareto (80/20)", "🌍  Expansión Geográfica", "🏆  Scorecard Directivo"], label_visibility="collapsed")

    last_date_str = "Fecha Desconocida"
    if not df_daily.empty:
        ed = df_daily["date"].max()
        last_date_str = f"{ed.day} de {meses_es_dict.get(ed.month, '')} de {ed.year}"

    st.markdown(f"""
    <div style="margin-top: 40px; padding: 16px; border-radius: 10px; background: #0C0C18; border: 1px solid #1E1E32; border-left: 3px solid #00FF88;">
        <p style="font-size: 10px; color: #8888AA; font-family: 'JetBrains Mono', monospace; margin: 0; text-transform: uppercase; letter-spacing: 0.1em;">Última Transacción</p>
        <p style="font-size: 14px; color: #00FF88; font-weight: 600; margin: 6px 0 0 0;">📅 {last_date_str}</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# VISTA 1 — RESUMEN EJECUTIVO 
# ══════════════════════════════════════════════
if "Resumen" in view and not df_daily.empty:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ GLOBAL SALES INTELLIGENCE</div>
        <div class="header-title">Resumen Ejecutivo</div>
        <div class="header-subtitle">Monitoreo de promedios operativos diarios y deltas de control versus períodos anteriores</div>
    </div>
    """, unsafe_allow_html=True)

    t_0 = df_daily["date"].max()
    t_1 = t_0 - pd.Timedelta(days=1)
    m_1 = t_0 - pd.DateOffset(months=1)
    y_1 = t_0 - pd.DateOffset(years=1)

    def get_row(dt):
        r = df_daily[df_daily["date"] == dt]
        return r.iloc[0] if not r.empty else None

    r_0, r_1, r_m, r_y = get_row(t_0), get_row(t_1), get_row(m_1), get_row(y_1)

    last_month_data = df_daily[(df_daily["date"].dt.month == t_0.month) & (df_daily["date"].dt.year == t_0.year)]
    avg_rev_daily = last_month_data["total_sales_revenue"].mean()
    avg_vol_daily = last_month_data["total_sales_volume"].mean()
    avg_tkt_daily = last_month_data["unit_revenue"].mean()

    def html_delta(val_0, val_ref, is_money=False):
        if val_0 is None or val_ref is None or val_ref == 0: return '<td class="delta-val neutro">0 (0%)</td>'
        diff = val_0 - val_ref
        pct = (diff / val_ref) * 100
        cls = "up" if diff >= 0 else "down"
        return f'<td class="delta-val {cls}">{fmt_num(diff, is_money, show_sign=True)} ({fmt_pct(pct)})</td>'

    v_rev = r_0["total_sales_revenue"] if r_0 is not None else 0
    v_vol = r_0["total_sales_volume"] if r_0 is not None else 0
    v_tkt = r_0["unit_revenue"] if r_0 is not None else 0
    
    # Active cities leídas directamente desde df_daily
    c_0_val = r_0["active_cities"] if r_0 is not None and "active_cities" in r_0 else 0
    c_1_val = r_1["active_cities"] if r_1 is not None and "active_cities" in r_1 else 0
    c_m_val = r_m["active_cities"] if r_m is not None and "active_cities" in r_m else 0
    c_y_val = r_y["active_cities"] if r_y is not None and "active_cities" in r_y else 0

    m_sel = st.session_state.get("metric_radio", "Ingresos")
    def get_card_style(metric_name, base_color):
        return f"border: 2px solid {base_color}; box-shadow: 0 0 15px {base_color}22;" if m_sel == metric_name else "border: 1px solid #25253A;"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card blue" style="{get_card_style('Ingresos', '#00D4FF')}">
            <div class="kpi-label">Rev. Promedio Diario</div>
            <div class="kpi-value blue">{fmt_num(avg_rev_daily, is_currency=True)}</div>
            <table class="delta-table-mini">
                <tr><td class="delta-lbl">vs Día Ant.</td>{html_delta(v_rev, r_1["total_sales_revenue"] if r_1 is not None else None, True)}</tr>
                <tr><td class="delta-lbl">vs Mes Ant.</td>{html_delta(v_rev, r_m["total_sales_revenue"] if r_m is not None else None, True)}</tr>
                <tr><td class="delta-lbl">vs Año Ant.</td>{html_delta(v_rev, r_y["total_sales_revenue"] if r_y is not None else None, True)}</tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card green" style="{get_card_style('Volumen', '#00FF88')}">
            <div class="kpi-label">Vol. Promedio Diario</div>
            <div class="kpi-value green">{fmt_num(avg_vol_daily)} u.</div>
            <table class="delta-table-mini">
                <tr><td class="delta-lbl">vs Día Ant.</td>{html_delta(v_vol, r_1["total_sales_volume"] if r_1 is not None else None)}</tr>
                <tr><td class="delta-lbl">vs Mes Ant.</td>{html_delta(v_vol, r_m["total_sales_volume"] if r_m is not None else None)}</tr>
                <tr><td class="delta-lbl">vs Año Ant.</td>{html_delta(v_vol, r_y["total_sales_volume"] if r_y is not None else None)}</tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card purple" style="{get_card_style('Ticket', '#BB66FF')}">
            <div class="kpi-label">Ticket Prom. Diario</div>
            <div class="kpi-value purple">{fmt_num(avg_tkt_daily, is_currency=True)}</div>
            <table class="delta-table-mini">
                <tr><td class="delta-lbl">vs Día Ant.</td>{html_delta(v_tkt, r_1["unit_revenue"] if r_1 is not None else None, True)}</tr>
                <tr><td class="delta-lbl">vs Mes Ant.</td>{html_delta(v_tkt, r_m["unit_revenue"] if r_m is not None else None, True)}</tr>
                <tr><td class="delta-lbl">vs Año Ant.</td>{html_delta(v_tkt, r_y["unit_revenue"] if r_y is not None else None, True)}</tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    def html_geo_delta(val_0, val_ref):
        if val_0 is None or val_ref is None or val_ref == 0: return '<td class="delta-val neutro">0</td>'
        diff = val_0 - val_ref
        cls = "up" if diff >= 0 else "down"
        sign = "+" if diff >= 0 else ""
        return f'<td class="delta-val {cls}">{sign}{int(diff)}</td>'

    with c4:
        st.markdown(f"""
        <div class="kpi-card orange" style="{get_card_style('Ciudades', '#FF8800')}">
            <div class="kpi-label">Ciudades Activas Hoy</div>
            <div class="kpi-value orange">{int(c_0_val)} Ciudades</div>
            <table class="delta-table-mini">
                <tr><td class="delta-lbl">vs Día Ant.</td>{html_geo_delta(c_0_val, c_1_val)}</tr>
                <tr><td class="delta-lbl">vs Mes Ant.</td>{html_geo_delta(c_0_val, c_m_val)}</tr>
                <tr><td class="delta-lbl">vs Año Ant.</td>{html_geo_delta(c_0_val, c_y_val)}</tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin-bottom:20px;"></div>""", unsafe_allow_html=True)
    
    c_sel_m, c_title, c_sel_t = st.columns([6, 3, 3])
    with c_sel_m: st.radio("Métrica a Visualizar", ["Ingresos", "Volumen", "Ticket", "Ciudades"], key="metric_radio", horizontal=True, label_visibility="collapsed")
    with c_title:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 6px;">
            <div class="section-dot" style="margin-right: 10px;"></div>
            <div class="section-title" style="margin: 0; font-size: 15px;">Análisis Temporal</div>
        </div>
        """, unsafe_allow_html=True)
    with c_sel_t: time_res_resumen = st.radio("Resolución", ["Mensual", "Semanal", "Diario"], horizontal=True, label_visibility="collapsed", key="time_res_resumen")
    st.markdown("<br>", unsafe_allow_html=True)

    if m_sel == "Ingresos": target_col, is_curr, color_tema, color_fill, y_min = "total_sales_revenue", True, "#00D4FF", "rgba(0, 212, 255, 0.15)", 200000000
    elif m_sel == "Volumen": target_col, is_curr, color_tema, color_fill, y_min = "total_sales_volume", False, "#00FF88", "rgba(0, 255, 136, 0.15)", 700000
    elif m_sel == "Ticket": target_col, is_curr, color_tema, color_fill, y_min = "unit_revenue", True, "#BB66FF", "rgba(187, 102, 255, 0.15)", 250
    else: target_col, is_curr, color_tema, color_fill, y_min = "active_cities", False, "#FF8800", "rgba(255, 136, 0, 0.15)", 0

    df_trend = df_daily.copy()
    if time_res_resumen == "Semanal": df_trend = df_trend[df_trend["date"] >= (t_0 - pd.DateOffset(months=12))]
    elif time_res_resumen == "Diario": df_trend = df_trend[df_trend["date"] >= (t_0 - pd.DateOffset(weeks=12))]

    df_trend["year"] = df_trend["date"].dt.year
    df_trend["month_period"] = df_trend["date"].dt.to_period("M").dt.to_timestamp()
    df_trend["week_period"] = df_trend["date"].dt.to_period("W").dt.to_timestamp()

    if time_res_resumen == "Mensual":
        df_g1 = df_trend.groupby("year")[target_col].mean().reset_index()
        df_g2 = df_trend.groupby("month_period")[target_col].mean().reset_index()
        x1, x2, t1, t2 = "year", "month_period", "POR AÑO", "POR MES"
    elif time_res_resumen == "Semanal":
        df_g1 = df_trend.groupby("month_period")[target_col].mean().reset_index()
        df_g2 = df_trend.groupby("week_period")[target_col].mean().reset_index()
        x1, x2, t1, t2 = "month_period", "week_period", "POR MES", "POR SEMANA"
    else:
        df_g1 = df_trend.groupby("week_period")[target_col].mean().reset_index()
        df_g2 = df_trend.groupby("date")[target_col].mean().reset_index()
        x1, x2, t1, t2 = "week_period", "date", "POR SEMANA", "POR DÍA"

    max_y1 = df_g1[target_col].max() if not df_g1.empty else 0
    max_y2 = df_g2[target_col].max() if not df_g2.empty else 0
    global_max = max(max_y1 if not pd.isna(max_y1) else 0, max_y2 if not pd.isna(max_y2) else 0)
    y_range = [y_min, max(y_min * 1.05, global_max * 1.1)] if global_max > 0 else None

    col_l, col_r = st.columns([2, 3])
    with col_l:
        st.markdown(f"""<p style="font-size:12px; color:#8888AA; font-weight:600; text-transform:uppercase; margin-bottom:5px;">• {m_sel} {t1}</p>""", unsafe_allow_html=True)
        custom_g1 = [fmt_num(v, is_curr) for v in df_g1[target_col]]
        fig_g1 = go.Figure(go.Bar(x=df_g1[x1].astype(str) if x1 == "year" else df_g1[x1], y=df_g1[target_col], marker=dict(color=df_g1[target_col], colorscale=[[0, "#151525"], [1, color_tema]], line=dict(width=0)), text=custom_g1, textposition="outside", textfont=dict(size=11, color=color_tema, family="JetBrains Mono"), customdata=custom_g1, hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>", width=0.6 if x1 == "year" else None))
        fig_g1.update_layout(PLOT_LAYOUT); fig_g1.update_layout(height=260, xaxis=dict(type="category" if x1 == "year" else "date"), yaxis=dict(showticklabels=False, showgrid=False))
        if y_range: fig_g1.update_yaxes(range=y_range)
        st.plotly_chart(fig_g1, use_container_width=True)

    with col_r:
        st.markdown(f"""<p style="font-size:12px; color:#8888AA; font-weight:600; text-transform:uppercase; margin-bottom:5px;">• {m_sel} {t2}</p>""", unsafe_allow_html=True)
        df_g2 = df_g2.sort_values(x2)
        custom_g2 = [fmt_num(v, is_curr) for v in df_g2[target_col]]
        df_g2["ma"] = df_g2[target_col].rolling(3).mean()
        custom_ma = [fmt_num(v, is_curr) if not pd.isna(v) else "0" for v in df_g2["ma"]]

        fig_g2 = go.Figure()
        fig_g2.add_trace(go.Scatter(x=df_g2[x2], y=df_g2[target_col], fill="tozeroy", fillcolor=color_fill, line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
        fig_g2.add_trace(go.Scatter(x=df_g2[x2], y=df_g2[target_col], mode="lines", line=dict(color=color_tema, width=2.5), name="Promedio", customdata=custom_g2, hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
        fig_g2.add_trace(go.Scatter(x=df_g2[x2], y=df_g2["ma"], mode="lines", line=dict(color="#FF8800", width=1.5, dash="dot"), name="Tendencia MA", customdata=custom_ma, hovertemplate="MA 3: %{customdata}<extra></extra>"))
        fig_g2.update_layout(PLOT_LAYOUT); fig_g2.update_layout(height=260, legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"))
        if y_range: fig_g2.update_yaxes(range=y_range)
        st.plotly_chart(fig_g2, use_container_width=True)

# ══════════════════════════════════════════════
# VISTA 2 — CAUSA RAÍZ (DEEP DIVE)
# ══════════════════════════════════════════════
elif "Causa" in view and not df_deep_dive.empty:
    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ DEEP DIVE ANALÍTICO</div>
        <div class="header-title">Análisis de Causa Raíz</div>
        <div class="header-subtitle">Composición y variación temporal (Promedios Diarios) para identificar orígenes de anomalías cruzadas</div>
    </div>
    """, unsafe_allow_html=True)

    c_m, c_t, c_ym = st.columns([1, 1, 1])
    with c_m: metrica_dd = st.selectbox("Métrica Total", ["Ingresos", "Volumen", "Ticket"])
    with c_t: tiempo_dd = st.selectbox("Resolución Temporal", ["Anual", "Mensual", "Semanal", "Diaria"])
    
    unique_ym = df_daily["date"].dt.to_period("M").unique()
    unique_ym_sorted = sorted(unique_ym, reverse=True)
    ym_options = ["Actual"] + [f"{ym.year}-{meses_es_dict.get(ym.month, '')}" for ym in unique_ym_sorted]
    with c_ym: ym_sel = st.selectbox("Período Base", ym_options)

    df_base = df_deep_dive.copy()
    col_geo, col_prod = st.columns([2, 3])
    with col_geo:
        st.markdown('<p style="font-size:11px; color:#00D4FF; font-weight:700; margin: 10px 0 5px 0; letter-spacing:0.05em;">🌍 FILTROS GEOGRÁFICOS</p>', unsafe_allow_html=True)
        cg1, cg2 = st.columns(2)
        paises = ["Todos"] + sorted(df_base["country"].dropna().unique())
        f_pais = cg1.selectbox("País", paises, label_visibility="collapsed")
        if f_pais != "Todos": df_base = df_base[df_base["country"] == f_pais]
        ciudades = ["Todos"] + sorted(df_base["city"].dropna().unique())
        f_ciudad = cg2.selectbox("Ciudad", ciudades, label_visibility="collapsed")
        if f_ciudad != "Todos": df_base = df_base[df_base["city"] == f_ciudad]

    with col_prod:
        st.markdown('<p style="font-size:11px; color:#00FF88; font-weight:700; margin: 10px 0 5px 0; letter-spacing:0.05em;">📦 FILTROS DE CATÁLOGO</p>', unsafe_allow_html=True)
        cp1, cp2, cp3 = st.columns(3)
        familias = ["Todos"] + sorted(df_base["product_family"].dropna().unique())
        f_fam = cp1.selectbox("Familia", familias, label_visibility="collapsed")
        if f_fam != "Todos": df_base = df_base[df_base["product_family"] == f_fam]
        categorias = ["Todos"] + sorted(df_base["product_category"].dropna().unique())
        f_cat = cp2.selectbox("Categoría", categorias, label_visibility="collapsed")
        if f_cat != "Todos": df_base = df_base[df_base["product_category"] == f_cat]
        productos = ["Todos"] + sorted(df_base["number_id"].dropna().unique())
        f_prod = cp3.selectbox("Producto", productos, label_visibility="collapsed")
        if f_prod != "Todos": df_base = df_base[df_base["number_id"] == f_prod]

    st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin: 15px 0 20px 0;"></div>""", unsafe_allow_html=True)

    c_modo, c_leyenda, _ = st.columns([3, 2, 3])
    with c_modo: modo_analisis = st.radio("Modo de Análisis", ["Valores Promedio Diario", "Variación Promedio (%)"], horizontal=True, label_visibility="collapsed")
    with c_leyenda: leyenda_tipo = st.radio("Perspectiva Leyenda", ["Producto", "Geográfico"], horizontal=True, label_visibility="collapsed")

    if leyenda_tipo == "Geográfico": nivel_dd = "country" if f_pais == "Todos" else "city"; nivel_dd_raw = "País" if f_pais == "Todos" else "Ciudad"
    else:
        if f_fam == "Todos": nivel_dd = "product_family"; nivel_dd_raw = "Familia"
        elif f_cat == "Todos": nivel_dd = "product_category"; nivel_dd_raw = "Categoría"
        else: nivel_dd = "number_id"; nivel_dd_raw = "Producto"

    is_curr = (metrica_dd in ["Ingresos", "Ticket"])
    t_max_global = df_daily["date"].max()
    ref_date = t_max_global if ym_sel == "Actual" else pd.to_datetime(f"{ym_sel.split('-')[0]}-{list(meses_es_dict.keys())[list(meses_es_dict.values()).index(ym_sel.split('-')[1])]}-01") + pd.offsets.MonthEnd(1)
    if ref_date > t_max_global: ref_date = t_max_global

    df_base = df_base[df_base["date"] <= ref_date]
    df_daily_filtered = df_daily[df_daily["date"] <= ref_date].copy()

    if tiempo_dd == "Mensual":
        start_date = (ref_date - pd.DateOffset(months=11)).replace(day=1)
        df_base = df_base[df_base["date"] >= start_date]; df_daily_filtered = df_daily_filtered[df_daily_filtered["date"] >= start_date]
    elif tiempo_dd == "Semanal":
        start_date = ref_date - pd.DateOffset(weeks=12)
        df_base = df_base[df_base["date"] > start_date]; df_daily_filtered = df_daily_filtered[df_daily_filtered["date"] > start_date]
    elif tiempo_dd == "Diaria":
        start_date = ref_date - pd.DateOffset(days=31)
        df_base = df_base[df_base["date"] > start_date]; df_daily_filtered = df_daily_filtered[df_daily_filtered["date"] > start_date]

    df_base["t_col"] = df_base["date"].dt.year.astype(str) if tiempo_dd == "Anual" else (df_base["date"].dt.to_period("M").dt.to_timestamp() if tiempo_dd == "Mensual" else (df_base["date"].dt.to_period("W").dt.to_timestamp() if tiempo_dd == "Semanal" else df_base["date"]))
    df_daily_filtered["t_col"] = df_daily_filtered["date"].dt.year.astype(str) if tiempo_dd == "Anual" else (df_daily_filtered["date"].dt.to_period("M").dt.to_timestamp() if tiempo_dd == "Mensual" else (df_daily_filtered["date"].dt.to_period("W").dt.to_timestamp() if tiempo_dd == "Semanal" else df_daily_filtered["date"]))

    days_dict = df_daily_filtered.groupby("t_col")["date"].nunique().to_dict()
    df_group = df_base.groupby(["t_col", nivel_dd])[["sales_revenue", "sales_volume"]].sum().reset_index()
    df_group["days"] = df_group["t_col"].map(days_dict).fillna(1).replace(0, 1)
    
    if metrica_dd == "Ingresos": df_group["avg_val"] = df_group["sales_revenue"] / df_group["days"]
    elif metrica_dd == "Volumen": df_group["avg_val"] = df_group["sales_volume"] / df_group["days"]
    else: df_group["avg_val"] = df_group["sales_revenue"] / df_group["sales_volume"]

    df_group.sort_values([nivel_dd, "t_col"], inplace=True)
    df_group["fmt_val"] = df_group["avg_val"].apply(lambda x: fmt_num(x, is_curr))

    if modo_analisis == "Variación Promedio (%)":
        df_group['pct_change'] = df_group.groupby(nivel_dd)['avg_val'].pct_change() * 100
        df_group['pct_change'] = df_group['pct_change'].replace([np.inf, -np.inf], 0).fillna(0)
        df_group['fmt_pct'] = df_group['pct_change'].apply(fmt_pct)

    unique_levels = sorted(df_group[nivel_dd].unique())
    color_map = {lvl: INDUSTRIAL_COLORS[i % len(INDUSTRIAL_COLORS)] for i, lvl in enumerate(unique_levels)}

    col_pie, col_bar = st.columns([1, 2.5])
    with col_pie:
        st.markdown(f"""<p style="font-size:12px; color:#8888AA; font-weight:600; text-transform:uppercase; margin-bottom:5px; text-align:center;">• SHARE GLOBAL: {nivel_dd_raw}</p>""", unsafe_allow_html=True)
        df_pie = df_group.groupby(nivel_dd)['avg_val'].mean().reset_index()
        fig_pie = px.pie(df_pie, values='avg_val', names=nivel_dd, color=nivel_dd, hole=0.45, color_discrete_map=color_map)
        fig_pie.update_traces(textposition='inside', textinfo='percent', hovertemplate="<b>%{label}</b><br>%{value}<extra></extra>", marker=dict(line=dict(color='#090910', width=2)))
        fig_pie.update_layout(PLOT_LAYOUT); fig_pie.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10), showlegend=True, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.markdown(f"""<p style="font-size:12px; color:#8888AA; font-weight:600; text-transform:uppercase; margin-bottom:5px;">• {metrica_dd} POR {nivel_dd_raw.upper()} ({tiempo_dd})</p>""", unsafe_allow_html=True)
        if modo_analisis == "Valores Promedio Diario":
            b_mode = "group" if metrica_dd == "Ticket" else "stack"
            fig_bar = px.bar(df_group, x="t_col", y="avg_val", color=nivel_dd, custom_data=["fmt_val", nivel_dd], color_discrete_map=color_map, barmode=b_mode)
            fig_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{customdata[1]}: %{customdata[0]}<extra></extra>", marker_line_width=0)
            y_title = "Valor Promedio Diario" if metrica_dd != "Ticket" else "Ticket Promedio"
        else:
            fig_bar = px.bar(df_group, x="t_col", y="pct_change", color=nivel_dd, custom_data=["fmt_pct", nivel_dd, "fmt_val"], color_discrete_map=color_map, barmode="group")
            fig_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{customdata[1]}: %{customdata[0]}<br>Promedio: %{customdata[2]}<extra></extra>", marker_line_width=0)
            y_title = "Variación vs Período Anterior (%)"
        fig_bar.update_layout(PLOT_LAYOUT); fig_bar.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="", yaxis_title=y_title)
        if tiempo_dd == "Anual": fig_bar.update_xaxes(type="category")
        st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════════
# VISTA 3 — PRODUCTOS & PARETO 
# ══════════════════════════════════════════════
elif "Pareto" in view and not df_deep_dive.empty:

    st.markdown("""
    <div class="main-header">
        <div class="header-eyebrow">◈ CATÁLOGO & RENDIMIENTO</div>
        <div class="header-title">Análisis de Pareto (80/20)</div>
        <div class="header-subtitle">Identificación dinámica de los elementos clave que traccionan los resultados del negocio</div>
    </div>
    """, unsafe_allow_html=True)

    df_base = df_deep_dive.copy()
    col_persp, col_geo, col_prod = st.columns([2, 2, 3])
    with col_persp:
        st.markdown('<p style="font-size:11px; color:#BB66FF; font-weight:700; margin: 10px 0 5px 0; letter-spacing:0.05em;">🎯 ANÁLISIS</p>', unsafe_allow_html=True)
        c_met, c_lvl = st.columns(2)
        metrica_pareto = c_met.selectbox("Métrica", ["Ingresos", "Volumen"], label_visibility="collapsed")
        nivel_opciones = {"Familia": "product_family", "Categoría": "product_category", "Producto": "number_id", "País": "country", "Ciudad": "city"}
        nivel_pareto_raw = c_lvl.selectbox("Perspectiva", list(nivel_opciones.keys()), label_visibility="collapsed"); nivel_pareto = nivel_opciones[nivel_pareto_raw]

    with col_geo:
        st.markdown('<p style="font-size:11px; color:#00D4FF; font-weight:700; margin: 10px 0 5px 0; letter-spacing:0.05em;">🌍 FILTROS GEOGRÁFICOS</p>', unsafe_allow_html=True)
        cg1, cg2 = st.columns(2)
        paises = ["Todos"] + sorted(df_base["country"].dropna().unique()); f_pais = cg1.selectbox("País", paises, key="p_pais", label_visibility="collapsed")
        if f_pais != "Todos": df_base = df_base[df_base["country"] == f_pais]
        ciudades = ["Todos"] + sorted(df_base["city"].dropna().unique()); f_ciudad = cg2.selectbox("Ciudad", ciudades, key="p_ciu", label_visibility="collapsed")
        if f_ciudad != "Todos": df_base = df_base[df_base["city"] == f_ciudad]

    with col_prod:
        st.markdown('<p style="font-size:11px; color:#00FF88; font-weight:700; margin: 10px 0 5px 0; letter-spacing:0.05em;">📦 FILTROS DE CATÁLOGO</p>', unsafe_allow_html=True)
        cp1, cp2, cp3 = st.columns(3)
        familias = ["Todos"] + sorted(df_base["product_family"].dropna().unique()); f_fam = cp1.selectbox("Familia", familias, key="p_fam", label_visibility="collapsed")
        if f_fam != "Todos": df_base = df_base[df_base["product_family"] == f_fam]
        categorias = ["Todos"] + sorted(df_base["product_category"].dropna().unique()); f_cat = cp2.selectbox("Categoría", categorias, key="p_cat", label_visibility="collapsed")
        if f_cat != "Todos": df_base = df_base[df_base["product_category"] == f_cat]
        productos = ["Todos"] + sorted(df_base["number_id"].dropna().unique()); f_prod = cp3.selectbox("Producto", productos, key="p_prod", label_visibility="collapsed")
        if f_prod != "Todos": df_base = df_base[df_base["number_id"] == f_prod]

    st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin: 15px 0 25px 0;"></div>""", unsafe_allow_html=True)

    target_col = 'sales_revenue' if metrica_pareto == 'Ingresos' else 'sales_volume'; is_curr = (metrica_pareto == 'Ingresos'); hdr_val = "INGRESOS" if metrica_pareto == "Ingresos" else "VOLUMEN"
    df_p = df_base.groupby(nivel_pareto)[target_col].sum().reset_index().sort_values(target_col, ascending=False).reset_index(drop=True)
    total_val = df_p[target_col].sum()
    df_p['cumulative_percentage'] = (df_p[target_col].cumsum() / total_val) * 100 if total_val > 0 else 0

    total_items = len(df_p); top1 = df_p.iloc[0][nivel_pareto] if total_items > 0 else "-"
    cats_to_80 = (df_p["cumulative_percentage"] <= 80).sum() + 1 if total_items > 0 else 0
    top3_share = (df_p.head(3)[target_col].sum() / total_val * 100) if total_val > 0 else 0
    bottom_count = int(np.ceil(total_items * 0.10)) if total_items > 0 else 0
    bottom10_share = (df_p.tail(bottom_count)[target_col].sum() / total_val * 100) if total_val > 0 and bottom_count > 0 else 0
    lbl_item = nivel_pareto_raw if bottom_count == 1 else {"País": "Países", "Ciudad": "Ciudades", "Familia": "Familias", "Categoría": "Categorías", "Producto": "Productos"}.get(nivel_pareto_raw, "elementos")

    font_size_lider = "20px" if len(str(top1)) > 12 else "28px"
    col_kp1, col_kp2, col_kp3, col_kp4 = st.columns(4)
    with col_kp1: st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Líder ({nivel_pareto_raw})</div><div class="kpi-value blue" style="text-align:center; font-size:{font_size_lider};">{top1}</div></div>', unsafe_allow_html=True)
    with col_kp2: st.markdown(f'<div class="kpi-card green"><div class="kpi-label">Para el 80% del Total</div><div class="kpi-value green" style="text-align:center;">{cats_to_80} de {total_items}</div></div>', unsafe_allow_html=True)
    with col_kp3: st.markdown(f'<div class="kpi-card purple"><div class="kpi-label">Share Top 3</div><div class="kpi-value purple" style="text-align:center;">{fmt_num(top3_share)}%</div></div>', unsafe_allow_html=True)
    with col_kp4: st.markdown(f'<div class="kpi-card orange"><div class="kpi-label">Share Bottom 10% ({bottom_count} {lbl_item})</div><div class="kpi-value orange" style="text-align:center;">{fmt_num(bottom10_share)}%</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
    tab_grafico, tab_tabla = st.tabs(["📊 Gráfico de Pareto", "📋 Tabla de Datos"])

    with tab_grafico:
        custom_pareto_val = [fmt_num(v, is_curr) for v in df_p[target_col]]; custom_pareto_pct = [f"{fmt_num(v)}%" for v in df_p["cumulative_percentage"]]
        fig_pareto = go.Figure(); bar_colors = [f"rgba(0, 212, 255, {max(0.2, 1 - i*0.05)})" for i in range(len(df_p))]
        fig_pareto.add_trace(go.Bar(x=df_p[nivel_pareto].astype(str), y=df_p[target_col], name="Valor", marker=dict(color=bar_colors, line=dict(width=0)), yaxis="y", customdata=custom_pareto_val, hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
        fig_pareto.add_trace(go.Scatter(x=df_p[nivel_pareto].astype(str), y=df_p["cumulative_percentage"], name="% Acumulado", mode="lines+markers", line=dict(color="#00FF88", width=2.5), marker=dict(size=7, color="#00FF88", symbol="diamond", line=dict(color="#090910", width=1.5)), yaxis="y2", customdata=custom_pareto_pct, hovertemplate="%{customdata} acumulado<extra></extra>"))
        fig_pareto.add_hline(y=80, line_dash="dot", line_color="rgba(255, 71, 87, 0.25)", annotation_text="  Umbral 80%", annotation_font_color="#FF4757", annotation_font_size=11, yref="y2")
        fig_pareto.update_layout(PLOT_LAYOUT); fig_pareto.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10), xaxis=dict(type="category"), yaxis=dict(title=metrica_pareto), yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 110], ticksuffix="%", tickfont=dict(size=11, color="#9090B0", family="JetBrains Mono"), gridcolor="rgba(0,0,0,0)", zeroline=False), bargap=0.25)
        st.plotly_chart(fig_pareto, use_container_width=True)

    with tab_tabla:
        rows_html = ""
        for i, row in df_p.iterrows():
            is_vital = "✓ VITAL" if row["cumulative_percentage"] <= 80 else "TRIVIAL"; vital_color = "#00FF88" if row["cumulative_percentage"] <= 80 else "#606080"
            rows_html += f"""<tr><td><span class="rank-badge">#{i+1:02d}</span></td><td style="color:#E0E0F0;font-weight:500;">{row[nivel_pareto]}</td><td style="color:#00D4FF;font-family:'JetBrains Mono',monospace;">{fmt_num(row[target_col], is_curr)}</td><td style="font-family:'JetBrains Mono',monospace;">{fmt_num(row['cumulative_percentage'])}%</td><td style="color:{vital_color};font-size:11px;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;">{is_vital}</td></tr>"""
        st.markdown(f"""<div class="chart-panel"><table class="data-table"><thead><tr><th>#</th><th>{nivel_pareto_raw.upper()}</th><th>{hdr_val}</th><th>ACUM.</th><th>CLASE</th></tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# VISTA 4 — EXPANSIÓN GEOGRÁFICA (Pura Lectura)
# ══════════════════════════════════════════════
elif "Geográfica" in view:
    
    ALTURA_GRAFICO         = 380  
    MARGEN_SUPERIOR_TABLA  = 10   
    ALTO_FILA_PAISES       = 46   
    ALTO_FILA_CIUDADES     = 38   

    if df_geo_summary.empty:
        st.warning("⚠️ Requiere ejecutar el ETL para generar 'ft_geo_summary.csv'.")
    else:
        cont_top = st.container()
        cont_mid = st.container()
        cont_bot = st.container()

        with cont_mid:
            st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin: 0px 0 0px 0;"></div>""", unsafe_allow_html=True)
            c_met, c_ym = st.columns([2, 4])
            
            with c_met:
                st.markdown('<p style="font-size:11px; color:#BB66FF; font-weight:700; margin: 5px 0 5px 0; letter-spacing:0.05em;">🎯 ANÁLISIS GLOBAL</p>', unsafe_allow_html=True)
                metrica_geo = st.radio("Métrica", ["Ingresos", "Volumen", "Ticket"], horizontal=True, label_visibility="collapsed")
            
            with c_ym:
                st.markdown('<p style="font-size:11px; color:#00D4FF; font-weight:700; margin: 5px 0 5px 0; letter-spacing:0.05em;">📅 AÑO BASE</p>', unsafe_allow_html=True)
                years_avail = sorted(df_geo_summary['year'].unique(), reverse=True)
                year_sel = st.selectbox("Año Base", years_avail, label_visibility="collapsed")
                
            st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin: 5px 0 15px 0;"></div>""", unsafe_allow_html=True)

        is_curr = (metrica_geo in ["Ingresos", "Ticket"])
        df_g = df_geo_summary[(df_geo_summary['year'] == year_sel) & (df_geo_summary['metric'] == metrica_geo)].copy()

        df_countries = df_g[df_g['loc_type'] == 'country'].nlargest(10, 'avg_val').sort_values('avg_val')
        df_cities_all = df_g[df_g['loc_type'] == 'city'].sort_values('avg_val', ascending=False)
        df_cities = pd.concat([df_cities_all.head(5), df_cities_all.tail(5)]).sort_values('avg_val', ascending=True) if len(df_cities_all) > 10 else df_cities_all

        def build_geo_table_v3(df_sorted, r_height, pad_top, w_fam="55%", w_cat="45%"):
            df_rev = df_sorted.iloc[::-1]
            rows = ""
            for _, row in df_rev.iterrows():
                f_html = re.sub(r'\((\d+°)\)', r'(<span style="color:#00D4FF; font-weight:700;">\1</span>)', str(row['best_family']))
                c_html = re.sub(r'\((\d+°)\)', r'(<span style="color:#00FF88; font-weight:700;">\1</span>)', str(row['best_category']))
                rows += f"<tr style='height: {r_height}px;'><td style='color:#D0D0E0; padding: 0 5px; width: {w_fam}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{f_html}</td><td style='color:#D0D0E0; padding: 0 5px; width: {w_cat}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{c_html}</td></tr>"
            return f"""<div style="padding-top: {pad_top}px; margin-top: 0px;"><table style="width: 100%; border-collapse: collapse; font-size: 11px; font-family: 'Inter', sans-serif; table-layout: fixed;"><tbody>{rows}</tbody></table></div>"""

        with cont_top:
            col_header, col_map = st.columns([3, 2])
            with col_header:
                st.markdown("""
                <div class="main-header" style="margin-bottom: 5px; padding: 15px 25px;">
                    <div class="header-eyebrow">◈ PRESENCIA GLOBAL</div>
                    <div class="header-title" style="font-size: 20px;">Expansión Geográfica</div>
                    <div class="header-subtitle">Análisis del mercado normalizado por alcance geográfico y ventaja comparativa</div>
                </div>
                """, unsafe_allow_html=True)
                
                top_c_str = df_countries.iloc[-1]['loc_name'] if not df_countries.empty else "-"
                top_ci_str = df_cities_all.iloc[0]['loc_name'] if not df_cities_all.empty else "-"

                c1, c2 = st.columns(2)
                with c1: st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">País Líder (Promedio)</div><div class="kpi-value blue" style="text-align:center; font-size: 24px;">{top_c_str}</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="kpi-card green"><div class="kpi-label">Ciudad Líder (Absoluto)</div><div class="kpi-value green" style="text-align:center; font-size: 24px;">{top_ci_str}</div></div>', unsafe_allow_html=True)
                    
            with col_map:
                df_map = df_g[df_g['loc_type'] == 'country'].copy()
                df_map["fmt_rev"] = df_map["avg_val"].apply(lambda x: fmt_num(x, is_curr))
                fig_map = px.choropleth(df_map, locations="loc_name", locationmode="country names", color="avg_val", hover_name="loc_name", hover_data={"avg_val": False, "fmt_rev": True, "loc_name": False}, color_continuous_scale=[[0, "#0A0A18"], [0.2, "#003344"], [0.5, "#006688"], [0.8, "#00AACC"], [1, "#00D4FF"]], labels={"fmt_rev": metrica_geo})
                fig_map.update_layout(PLOT_LAYOUT); fig_map.update_layout(height=180, coloraxis_showscale=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_map, use_container_width=True)

        with cont_bot:
            col_countries, col_cities = st.columns(2)

            with col_countries:
                cc_left, cc_right = st.columns([1.7, 0.9])
                custom_c = [fmt_num(v, is_curr) for v in df_countries["avg_val"]]
                with cc_left:
                    st.markdown(f"""<div class="section-header"><div class="section-dot" style="background:#00D4FF;box-shadow:0 0 8px #00D4FF;"></div><div class="section-title">PROMEDIO POR CIUDAD EN CADA PAÍS</div></div>""", unsafe_allow_html=True)
                    fig_countries = go.Figure(go.Bar(x=df_countries["avg_val"], y=df_countries["loc_name"], orientation="h", marker=dict(color=df_countries["avg_val"], colorscale=[[0, "#003344"], [1, "#00D4FF"]], line=dict(width=0)), text=custom_c, textposition="inside", insidetextanchor="end", textfont=dict(size=11, color="#FFFFFF", family="JetBrains Mono"), customdata=custom_c, hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
                    fig_countries.update_layout(PLOT_LAYOUT); fig_countries.update_layout(height=ALTURA_GRAFICO, margin=dict(l=0, r=0, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False), yaxis=dict(tickfont=dict(size=11, color="#D0D0E0")))
                    st.plotly_chart(fig_countries, use_container_width=True)
                    
                with cc_right:
                    st.markdown("""<div class="section-header" style="justify-content: space-between; border-bottom: 1px solid #1A1A2C; padding-bottom: 8px;"><div style="display: flex; align-items: center; gap: 8px; width: 55%;"><div class="section-dot" style="background:#00D4FF;box-shadow:0 0 8px #00D4FF;"></div><div class="section-title" style="font-size: 14px; font-weight: 700;">FAMILIA</div></div><div style="display: flex; align-items: center; gap: 8px; width: 45%;"><div class="section-dot" style="background:#00FF88;box-shadow:0 0 8px #00FF88;"></div><div class="section-title" style="font-size: 14px; font-weight: 700;">CATEGORÍA</div></div></div>""", unsafe_allow_html=True)
                    st.markdown(build_geo_table_v3(df_countries, ALTO_FILA_PAISES, MARGEN_SUPERIOR_TABLA, w_fam="55%", w_cat="45%"), unsafe_allow_html=True)

            with col_cities:
                cci_left, cci_right = st.columns([1.7, 0.9])
                custom_ci = [fmt_num(v, is_curr) for v in df_cities["avg_val"]]
                with cci_left:
                    st.markdown(f"""<div class="section-header"><div class="section-dot" style="background:#00FF88;box-shadow:0 0 8px #00FF88;"></div><div class="section-title">TOP 5 Y BOTTOM 5 CIUDADES (TOTAL)</div></div>""", unsafe_allow_html=True)
                    fig_cities = go.Figure(go.Bar(x=df_cities["avg_val"], y=df_cities["loc_name"], orientation="h", marker=dict(color=df_cities["avg_val"], colorscale=[[0, "#1A0033"], [1, "#AA44FF"]], line=dict(width=0)), text=custom_ci, textposition="inside", insidetextanchor="end", textfont=dict(size=11, color="#FFFFFF", family="JetBrains Mono"), customdata=custom_ci, hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
                    fig_cities.update_layout(PLOT_LAYOUT); fig_cities.update_layout(height=ALTURA_GRAFICO, margin=dict(l=0, r=0, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False), yaxis=dict(tickfont=dict(size=11, color="#D0D0E0")))
                    st.plotly_chart(fig_cities, use_container_width=True)
                    
                with cci_right:
                    st.markdown("""<div class="section-header" style="justify-content: space-between; border-bottom: 1px solid #1A1A2C; padding-bottom: 8px;"><div style="display: flex; align-items: center; gap: 8px; width: 45%;"><div class="section-dot" style="background:#00D4FF;box-shadow:0 0 8px #00D4FF;"></div><div class="section-title" style="font-size: 14px; font-weight: 700;">FAMILIA</div></div><div style="display: flex; align-items: center; gap: 8px; width: 55%;"><div class="section-dot" style="background:#00FF88;box-shadow:0 0 8px #00FF88;"></div><div class="section-title" style="font-size: 14px; font-weight: 700;">CATEGORÍA</div></div></div>""", unsafe_allow_html=True)
                    st.markdown(build_geo_table_v3(df_cities, ALTO_FILA_CIUDADES, MARGEN_SUPERIOR_TABLA, w_fam="45%", w_cat="55%"), unsafe_allow_html=True)

# ══════════════════════════════════════════════
# VISTA 5 — SCORECARD DIRECTIVO (Pura Lectura)
# ══════════════════════════════════════════════
elif "Scorecard" in view:

    if df_scorecard.empty:
        st.warning("⚠️ Requiere ejecutar el ETL para generar 'ft_scorecard.csv'.")
    else:
        st.markdown("""
        <div class="main-header">
            <div class="header-eyebrow">◈ RENDIMIENTO EXTREMO</div>
            <div class="header-title">Scorecard Directivo</div>
            <div class="header-subtitle">Análisis de máximos, mínimos y variaciones porcentuales frente al período inmediatamente anterior</div>
        </div>
        """, unsafe_allow_html=True)

        col_met, col_res, col_per = st.columns([2, 3, 3])
        with col_met:
            st.markdown('<p style="font-size:11px; color:#BB66FF; font-weight:700; margin: 0 0 5px 0; letter-spacing:0.05em;">🎯 MÉTRICA</p>', unsafe_allow_html=True)
            metrica_score = st.radio("Métrica", ["Ingresos", "Volumen"], horizontal=True, label_visibility="collapsed")
        with col_res:
            st.markdown('<p style="font-size:11px; color:#00D4FF; font-weight:700; margin: 0 0 5px 0; letter-spacing:0.05em;">⏳ RESOLUCIÓN TEMPORAL</p>', unsafe_allow_html=True)
            res_score = st.radio("Resolución", ["Anual", "Mensual", "Semanal", "Diaria"], horizontal=True, label_visibility="collapsed", key="score_res")

        df_s_filtered = df_scorecard[(df_scorecard['metrica'] == metrica_score) & (df_scorecard['resolucion'] == res_score)]
        # Tomamos los periodos únicos manteniendo el orden natural generado por el ETL
        period_opts = df_s_filtered['periodo'].unique()

        with col_per:
            st.markdown('<p style="font-size:11px; color:#00FF88; font-weight:700; margin: 0 0 5px 0; letter-spacing:0.05em;">📅 PERÍODO A ANALIZAR</p>', unsafe_allow_html=True)
            sel_per_str = st.selectbox("Período a Analizar", period_opts, label_visibility="collapsed")

        st.markdown("""<div style="width:100%; height:1px; background:#1A1A2C; margin: 15px 0 25px 0;"></div>""", unsafe_allow_html=True)

        df_target = df_s_filtered[df_s_filtered['periodo'] == sel_per_str].copy()
        is_curr = (metrica_score == 'Ingresos')

        def draw_score_row(title_card_html, data_df, kpi_names, kpi_vals, is_growth, color_cls):
            cols = st.columns([1.5, 2, 2, 2, 2])
            with cols[0]: st.markdown(title_card_html, unsafe_allow_html=True)
            
            dims = ['País', 'Ciudad', 'Familia', 'Categoría']
            for i, d in enumerate(dims):
                row = data_df[data_df['dimension'] == d]
                if row.empty: continue
                n = str(row.iloc[0][kpi_names])
                v = row.iloc[0][kpi_vals]
                v_str = fmt_pct_score(v) if is_growth else f"{fmt_num(v, is_curr)}/día"
                lbl_pfx = "Crecimiento: " if is_growth else ""
                
                with cols[i+1]:
                    st.markdown(f'<div class="kpi-card {color_cls}" style="min-height:95px;"><div class="kpi-label">{d}</div><div class="kpi-value {color_cls}" style="font-size:24px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;" title="{n}">{n}</div><div style="text-align:center; color:#A0A0C0; font-family:\'JetBrains Mono\', monospace; font-size:12px; font-weight:600;">{lbl_pfx}{v_str}</div></div>', unsafe_allow_html=True)

        # RENDER ROWS
        draw_score_row('<div class="kpi-card blue" style="background: #00D4FF15; border: 1px solid #00D4FF50; min-height:95px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-size:12px; font-weight:800; text-transform:uppercase; color:#00D4FF; line-height:1.4;">🏆<br>Mayores<br>Cantidades<br>(Prom. Diario)</div>', df_target, 'top_abs_name', 'top_abs_val', False, 'blue')
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
        draw_score_row('<div class="kpi-card green" style="background: #00FF8815; border: 1px solid #00FF8850; min-height:95px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-size:12px; font-weight:800; text-transform:uppercase; color:#00FF88; line-height:1.4;">🚀<br>Mayor<br>Crecimiento</div>', df_target, 'top_g_name', 'top_g_val', True, 'green')
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
        draw_score_row('<div class="kpi-card orange" style="background: #FF880015; border: 1px solid #FF880050; min-height:95px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-size:12px; font-weight:800; text-transform:uppercase; color:#FF8800; line-height:1.4;">⚠️<br>Menores<br>Cantidades<br>(Prom. Diario)</div>', df_target, 'bot_abs_name', 'bot_abs_val', False, 'orange')
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
        draw_score_row('<div class="kpi-card red" style="background: #FF475715; border: 1px solid #FF475750; min-height:95px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-size:12px; font-weight:800; text-transform:uppercase; color:#FF4757; line-height:1.4;">📉<br>Menor<br>Crecimiento<br>(Caída)</div>', df_target, 'bot_g_name', 'bot_g_val', True, 'red')