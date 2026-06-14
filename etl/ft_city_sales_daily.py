import pandas as pd
import os

def run():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    print("⏳ Generando ft_city_sales_daily (Radar geográfico temporal)...")
    try:
        # Usamos date y geo_id para las ventas, y geo_id y city para la dimensión
        ventas = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), usecols=["date", "geo_id"])
        ciudades = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"), usecols=["geo_id", "city"])
        
        # Cruzamos usando geo_id
        df = pd.merge(ventas, ciudades, on="geo_id", how="left")
        df['date'] = pd.to_datetime(df['date']).dt.floor('D')
        
        # Filtramos para quedarnos con combinaciones únicas de fecha y ciudad
        active_cities = df[['date', 'city']].drop_duplicates().reset_index(drop=True)
        
        active_cities.to_csv(os.path.join(PROCESSED_PATH, "ft_city_sales_daily.csv"), index=False)
        print(f"✅ ft_city_sales_daily.csv generado con éxito.")
    except Exception as e:
        print(f"❌ Error en ft_city_sales_daily: {e}")

if __name__ == "__main__":
    run()