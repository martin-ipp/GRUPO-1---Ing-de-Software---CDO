import os
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def transform():
    # 2. Buscar el archivo CSV de 10M en data/raw
    files = [f for f in os.listdir(RAW_PATH) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError("No hay archivos CSV en data/raw")

    latest = max(
        files, key=lambda f: os.path.getmtime(os.path.join(RAW_PATH, f))
    )
    print(f"🚀 Leyendo archivo original: {latest}...")

    df = pd.read_csv(os.path.join(RAW_PATH, latest))

    # 3. Normalizar columnas a minúsculas y guiones bajos
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Reemplazar el string "None" por un valor nulo real en la columna 'state'
    df["state"] = df["state"].replace("None", pd.NA)

    # 4. Crear el geo_id compuesto para la dimensión geográfica
    df["geo_id"] = df["latitude"].astype(str) + "_" + df["longitude"].astype(str)

    # 5. CREAR LA TABLA DIM_LOCATION (Dimensión Geográfica)
    print("📁 Creando tabla de dimensión 'dim_location'...")
    columnas_dim_loc = ["geo_id", "longitude", "latitude", "city", "state", "country"]
    dim_location = df[columnas_dim_loc].drop_duplicates(subset=["geo_id"]).reset_index(drop=True)

    # 6. CREAR LA TABLA DIM_PRODUCT (Abriendo el código del producto)
    print("📦 Creando tabla de dimensión 'dim_product' con lógica de negocio...")
    
    # Primero aislamos las columnas originales del producto de forma única
    dim_product = df[["product_id", "product_category"]].drop_duplicates(subset=["product_id"]).copy()
    
    # Aplicamos tu ingeniería: extraemos familia (primeras 4 letras) y número (últimos 4 caracteres)
    dim_product["product_family"] = dim_product["product_id"].str[:4]
    dim_product["number_id"] = dim_product["product_id"].str[4:]
    
    # Reordenamos las columnas como pediste
    columnas_producto = ["product_id", "number_id", "product_family", "product_category"]
    dim_product = dim_product[columnas_producto].reset_index(drop=True)

    # 7. MODIFICAR LA TABLA BASE DE HECHOS (sales_clean)
    print("✂️ Optimizando tabla de hechos (removiendo textos duplicados)...")
    df = df.rename(columns={"location_id": "transaction_id"})

    # Quitamos datos geográficos y la categoría del producto (ya viven en las dimensiones)
    columnas_a_borrar = ["city", "state", "country", "latitude", "longitude", "product_category"]
    df = df.drop(columns=columnas_a_borrar)

    # Formatear volúmenes y fechas
    df["sales_volume"] = df["sales_volume"].round(2)
    df["date"] = pd.to_datetime(df["date"])

    # 8. GUARDAR ARCHIVOS FINALES EN PROCESSED
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    print("💾 Guardando archivos del modelo estrella en 'data/processed'...")
    df.to_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), index=False)
    dim_location.to_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"), index=False)
    dim_product.to_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"), index=False)

    print(f"\n--- ✨ ¡Transformación de Arquitectura Completa! ---")
    print(f"📊 FACT (sales_clean.csv): {len(df):,} filas guardadas (solo IDs y métricas).")
    print(f"🗺️  DIM LOCATION (dim_location.csv): {len(dim_location):,} ubicaciones únicas.")
    print(f"📦 DIM PRODUCT (dim_product.csv): {len(dim_product):,} productos decodificados.")


if __name__ == "__main__":
    transform()