import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

def transform():
    # Tomar el CSV más reciente de data/raw
    files = [f for f in os.listdir(RAW_PATH) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError("No hay archivos CSV en data/raw")
    
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(RAW_PATH, f)))
    print(f"Procesando archivo: {latest}")
    
    df = pd.read_csv(os.path.join(RAW_PATH, latest))

    # Normalizar columnas
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Reemplazar "None" string por NaN real
    df["state"] = df["state"].replace("None", pd.NA)

    # Redondear sales_volume
    df["sales_volume"] = df["sales_volume"].round(2)

    # Convertir date a datetime
    df["date"] = pd.to_datetime(df["date"])

    # Guardar resultado
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    df.to_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), index=False)
    print(f"Transform OK — {len(df)} filas procesadas")

if __name__ == "__main__":
    transform()