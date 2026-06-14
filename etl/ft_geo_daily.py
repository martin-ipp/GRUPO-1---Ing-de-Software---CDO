import pandas as pd
import os

def run():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    print("⏳ Generando ft_geo_daily (Totales diarios por Geografía)...")
    try:
        # 1. Leer ventas (solo columnas necesarias para alivianar memoria)
        ventas = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), 
                             usecols=["date", "geo_id", "sales_revenue", "sales_volume"])
        ventas['date'] = pd.to_datetime(ventas['date']).dt.floor('D')
        
        # 2. Leer dimensión de locación
        ciudades = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"), 
                               usecols=["geo_id", "city", "country"])
        
        # 3. Cruzar datos
        df = pd.merge(ventas, ciudades, on="geo_id", how="left")
        
        # 4. Agrupar sumando los totales
        daily_geo = df.groupby(['date', 'country', 'city']).agg(
            total_sales_revenue=('sales_revenue', 'sum'),
            total_sales_volume=('sales_volume', 'sum')
        ).reset_index()
        
        daily_geo.to_csv(os.path.join(PROCESSED_PATH, "ft_geo_daily.csv"), index=False)
        print(f"✅ ft_geo_daily.csv generado con éxito ({len(daily_geo)} filas).")
    except Exception as e:
        print(f"❌ Error en ft_geo_daily: {e}")

if __name__ == "__main__":
    run()