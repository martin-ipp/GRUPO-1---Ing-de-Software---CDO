import pandas as pd
import os

def run():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    print("⏳ Generando ft_deep_dive (Cubo Maestro de Causa Raíz)...")
    try:
        ventas = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), 
                             usecols=["date", "product_id", "geo_id", "sales_revenue", "sales_volume"])
        ventas['date'] = pd.to_datetime(ventas['date']).dt.floor('D')
        
        productos = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"), 
                               usecols=["product_id", "number_id", "product_family", "product_category"])
                               
        geografia = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"), 
                               usecols=["geo_id", "city", "country"])
        
        df = pd.merge(ventas, productos, on="product_id", how="left")
        df = pd.merge(df, geografia, on="geo_id", how="left")
        
        # Agrupamos por la cruza TOTAL de dimensiones
        dd_cube = df.groupby(['date', 'country', 'city', 'product_family', 'product_category', 'number_id']).agg(
            sales_revenue=('sales_revenue', 'sum'),
            sales_volume=('sales_volume', 'sum')
        ).reset_index()
        
        dd_cube.to_csv(os.path.join(PROCESSED_PATH, "ft_deep_dive.csv"), index=False)
        print("✅ ft_deep_dive.csv generado con éxito.")
    except Exception as e:
        print(f"❌ Error en ft_deep_dive: {e}")

if __name__ == "__main__":
    run()