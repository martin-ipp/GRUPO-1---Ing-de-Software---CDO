import pandas as pd
import os

def run():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    print("⏳ Generando Dimensión Calendario (dim_date)...")
    
    try:
        # 1. Leer SOLO la columna de fechas de sales_clean
        ruta_sales = os.path.join(PROCESSED_PATH, "sales_clean.csv")
        df_dates = pd.read_csv(ruta_sales, usecols=["date"])
        df_dates["date"] = pd.to_datetime(df_dates["date"])
        
        # 2. Obtener límites
        fecha_min = df_dates["date"].min().floor('D') # Redondear al inicio del día
        fecha_max = df_dates["date"].max().floor('D')
        
        # 3. Generar calendario continuo
        calendario = pd.date_range(start=fecha_min, end=fecha_max, freq='D')
        dim_date = pd.DataFrame({"date": calendario})
        
        # 4. Enriquecer dimensión
        dim_date["year"] = dim_date["date"].dt.year
        dim_date["month"] = dim_date["date"].dt.month
        dim_date["day"] = dim_date["date"].dt.day
        dim_date["weekday_name"] = dim_date["date"].dt.day_name()
        dim_date["is_weekend"] = dim_date["date"].dt.dayofweek.isin([5, 6])
        
        # 5. Exportar
        ruta_salida = os.path.join(PROCESSED_PATH, "dim_date.csv")
        dim_date.to_csv(ruta_salida, index=False)
        print(f"✅ dim_date.csv generado con éxito ({len(dim_date)} días mapeados).")
        
    except Exception as e:
        print(f"❌ Error al generar dim_date: {e}")

if __name__ == "__main__":
    run()