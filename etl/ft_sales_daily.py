import pandas as pd
import numpy as np

def process_daily_sales(input_daily_path, input_city_path, output_path):
    # 1. Cargar los datos base
    df_daily = pd.read_csv(input_daily_path)
    df_city_daily = pd.read_csv(input_city_path)
    
    # 2. Asegurar formato de fecha
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    df_city_daily["date"] = pd.to_datetime(df_city_daily["date"])
    
    # 3. Calcular ciudades activas por día directamente en el ETL
    df_city_counts = df_city_daily.groupby("date")["city"].nunique().reset_index(name="active_cities")
    
    # 4. Unir y rellenar vacíos
    df_daily_final = pd.merge(df_daily, df_city_counts, on="date", how="left")
    df_daily_final["active_cities"] = df_daily_final["active_cities"].fillna(0).astype(int)
    
    # 5. Exportar listo para Streamlit
    df_daily_final.to_csv(output_path, index=False)
    print("✅ ft_sales_daily.csv actualizado con active_cities")