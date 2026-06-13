import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA (Modo Wide)
# ==========================================
st.set_page_config(page_title="CDO Global Intelligence", page_icon="📈", layout="wide")

# Estilos CSS personalizados para tarjetas y métricas
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. RUTA DINÁMICA DE DATOS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

@st.cache_data
def load_data(filename):
    ruta = os.path.join(PROCESSED_PATH, filename)
    try:
        return pd.read_csv(ruta)
    except FileNotFoundError:
        return pd.DataFrame()

# Cargamos el arsenal completo de datos
df_month = load_data("ft_transactions_per_month.csv")
df_year = load_data("ft_transactions_per_year.csv")
df_cat_pareto = load_data("ft_productcategory_pareto.csv")
df_prod_pareto = load_data("ft_product_pareto.csv")
df_products = load_data("ft_transactions_per_product.csv")
df_country = load_data("ft_transactions_per_country.csv")
df_weekday = load_data("ft_transactions_per_weekday.csv")
df_city = load_data("ft_transactions_per_city.csv")

# ==========================================
# 3. BARRA LATERAL EJECUTIVA
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=120)
st.sidebar.markdown("## 📊 CDO Analytics")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegación Estratégica:",
    [
        "🏢 Resumen Ejecutivo",
        "💎 Performance de Productos",
        "🌍 Mapa de Operaciones",
        "👥 Hábitos de Consumo"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("✅ Origen de Datos: Modelo Estrella Validado")

# ==========================================
# 4. VISTA 1: RESUMEN EJECUTIVO (KPIs MACRO)
# ==========================================
if menu == "🏢 Resumen Ejecutivo":
    st.title("🏢 Resumen Ejecutivo Financiero")
    st.markdown("Métricas clave de negocio e histórico de facturación.")

    if not df_year.empty and not df_country.empty:
        total_rev = df_year['total_sales_revenue'].sum()
        total_vol = df_year['total_sales_volume'].sum()
        aov = total_rev / total_vol if total_vol > 0 else 0
        top_country = df_country.loc[df_country['total_sales_revenue'].idxmax()]['country']

        # Fila de Tarjetas (Scorecards)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Ingresos Totales (Gross)", f"${total_rev:,.0f}")
        kpi2.metric("Unidades Vendidas", f"{total_vol:,.0f} u.")
        kpi3.metric("Ticket Promedio (AOV)", f"${aov:,.2f}")
        kpi4.metric("Mercado Líder", f"🏆 {top_country}")

        st.markdown("---")

        col_izq, col_der = st.columns([7, 3])
        
        with col_izq:
            st.subheader("📈 Evolución de Ingresos y Tendencia Mensual")
            fig_trend = px.area(
                df_month, x="date", y="total_sales_revenue", 
                labels={"date": "Periodo", "total_sales_revenue": "Ingresos USD"},
                color_discrete_sequence=['#2ecc71']
            )
            fig_trend.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_der:
            st.subheader("💡 Insights de Negocio")
            st.info(f"**Crecimiento:** La compañía acumula **${total_rev:,.0f}** en facturación histórica, sostenida por la venta de **{total_vol:,.0f}** unidades.")
            st.success(f"**Mercado:** La dependencia actual marca que el mercado de **{top_country}** es el motor principal de la rentabilidad.")
            st.warning("**Oportunidad:** El ticket promedio se mantiene estable, lo que sugiere espacio para estrategias de *upselling*.")

# ==========================================
# 5. VISTA 2: PRODUCTOS Y PARETO
# ==========================================
elif menu == "💎 Performance de Productos":
    st.title("💎 Rendimiento del Catálogo (Regla 80/20)")
    
    if not df_prod_pareto.empty:
        # Calcular el punto de corte del Pareto
        productos_top = df_prod_pareto[df_prod_pareto['cumulative_percentage'] <= 80]
        cant_total = len(df_prod_pareto)
        cant_top = len(productos_top)
        porcentaje_catalogo = (cant_top / cant_total) * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Productos Activos", f"{cant_total}")
        c2.metric("Productos Vitales (Generan el 80%)", f"{cant_top}")
        c3.metric("Eficiencia del Catálogo", f"{porcentaje_catalogo:.1f}% del stock genera el 80% de ganancia")

        st.markdown("---")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📉 Curva de Pareto por Producto")
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(
                x=df_prod_pareto['product_id'], y=df_prod_pareto['total_revenue'],
                name="Ingresos USD", marker_color="#34495e"
            ))
            fig_pareto.add_trace(go.Scatter(
                x=df_prod_pareto['product_id'], y=df_prod_pareto['cumulative_percentage'],
                name="% Acumulado", mode="lines+markers", marker=dict(color="#e74c3c"), yaxis="y2"
            ))
            fig_pareto.update_layout(
                template="plotly_white",
                yaxis=dict(title="Ingresos (USD)"),
                yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 110]),
                showlegend=False
            )
            fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Meta 80%", yref="y2")
            st.plotly_chart(fig_pareto, use_container_width=True)

        with col2:
            st.subheader("🏆 Top 5 Productos Estrella")
            top_5 = df_prod_pareto.head(5)[['product_id', 'total_revenue']]
            top_5.rename(columns={'product_id': 'Producto', 'total_revenue': 'Ingresos (USD)'}, inplace=True)
            st.dataframe(top_5.style.format({'Ingresos (USD)': '${:,.0f}'}), use_container_width=True, hide_index=True)
            
            st.info(f"🚨 **Alerta de Stock:** Es crítico asegurar el abastecimiento permanente de los **{cant_top} productos principales**, ya que cualquier quiebre de stock en estos ítems impactará directamente en el 80% de la facturación mensual.")

# ==========================================
# 6. VISTA 3: EXPANSIÓN GEOGRÁFICA
# ==========================================
elif menu == "🌍 Mapa de Operaciones":
    st.title("🌍 Distribución Global de Ventas")

    if not df_country.empty and not df_city.empty:
        col_mapa, col_datos = st.columns([6, 4])
        
        with col_mapa:
            st.subheader("Intensidad de Facturación por País")
            fig_map = px.choropleth(
                df_country, locations="country", locationmode="country names",
                color="total_sales_revenue", hover_name="country", 
                color_continuous_scale="Teal",
                labels={"total_sales_revenue": "Ingresos (USD)"}
            )
            fig_map.update_layout(geo=dict(showcoastlines=True), margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_map, use_container_width=True)

        with col_datos:
            st.subheader("🏙️ Top 10 Ciudades Estratégicas")
            top_cities = df_city.nlargest(10, "total_sales_revenue").sort_values("total_sales_revenue", ascending=True)
            fig_cities = px.bar(
                top_cities, x="total_sales_revenue", y="city", orientation="h", text_auto=".2s",
                labels={"total_sales_revenue": "Ingresos USD", "city": ""},
                color="total_sales_revenue", color_continuous_scale="Teal"
            )
            fig_cities.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_cities, use_container_width=True)

# ==========================================
# 7. VISTA 4: COMPORTAMIENTO DEL CONSUMIDOR
# ==========================================
elif menu == "👥 Hábitos de Consumo":
    st.title("👥 Análisis de Demanda Semanal")
    
    if not df_weekday.empty:
        orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        df_weekday['weekday_name'] = pd.Categorical(df_weekday['weekday_name'], categories=orden_dias, ordered=True)
        df_weekday = df_weekday.sort_values('weekday_name')
        
        mejor_dia = df_weekday.loc[df_weekday['total_sales_revenue'].idxmax()]['weekday_name']

        c1, c2 = st.columns([7, 3])
        with c1:
            fig_wd = px.bar(
                df_weekday, x="weekday_name", y="total_sales_revenue",
                labels={"weekday_name": "Día de la Semana", "total_sales_revenue": "Volumen de Ingresos USD"},
                color="total_sales_revenue", color_continuous_scale="Sunset"
            )
            fig_wd.update_layout(template="plotly_white")
            st.plotly_chart(fig_wd, use_container_width=True)
            
        with c2:
            st.subheader("💡 Conclusión de Demanda")
            st.success(f"🔥 El pico máximo de transacciones ocurre los días **{mejor_dia}**.")
            st.info("Recomendación: Enfocar las campañas de marketing y promociones especiales 24 horas antes del pico de consumo para maximizar la tasa de conversión.")