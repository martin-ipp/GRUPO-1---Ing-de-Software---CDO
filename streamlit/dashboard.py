import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

DB_URL = "postgresql://postgres:postgres@host.docker.internal:5432/pipeline_db"

st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
st.title("Dashboard de Ventas Globales")

@st.cache_data
def cargar_datos():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM sales_by_category", engine)
    return df

df = cargar_datos()

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Categorías", len(df))
col2.metric("Revenue Total", f"${df['total_revenue'].sum():,.0f}")
col3.metric("Transacciones Totales", f"{df['num_transactions'].sum():,}")

st.divider()

# Gráfico de revenue por categoría
st.subheader("Revenue por Categoría")
fig1 = px.bar(
    df.sort_values("total_revenue", ascending=False),
    x="product_category",
    y="total_revenue",
    color="total_revenue",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico de volumen por categoría
st.subheader("Volumen de Ventas por Categoría")
fig2 = px.pie(
    df,
    names="product_category",
    values="total_volume"
)
st.plotly_chart(fig2, use_container_width=True)