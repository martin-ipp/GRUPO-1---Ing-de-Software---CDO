import pandas as pd
import os

def run():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    print("⏳ Generando ft_product_daily (Totales diarios por Producto)...")
    try:
        # 1. Leer ventas (solo lo necesario)
        ventas = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), 
                             usecols=["date", "product_id", "sales_revenue", "sales_volume"])
        ventas['date'] = pd.to_datetime(ventas['date']).dt.floor('D')
        
        # 2. Leer dimensión de producto con tus columnas exactas
        productos = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"), 
                               usecols=["product_id", "number_id", "product_family", "product_category"])
        
        # 3. Cruzar datos
        df = pd.merge(ventas, productos, on="product_id", how="left")
        
        # 4. Agrupar sumando los TOTALES diarios
        daily_prod = df.groupby(['date', 'product_family', 'product_category', 'number_id']).agg(
            total_sales_revenue=('sales_revenue', 'sum'),
            total_sales_volume=('sales_volume', 'sum')
        ).reset_index()
        
        daily_prod.to_csv(os.path.join(PROCESSED_PATH, "ft_product_daily.csv"), index=False)
        print(f"✅ ft_product_daily.csv generado con éxito ({len(daily_prod)} filas).")
    except Exception as e:
        print(f"❌ Error en ft_product_daily: {e}")

if __name__ == "__main__":
    run()