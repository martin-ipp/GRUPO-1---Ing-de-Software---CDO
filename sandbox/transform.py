import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

def transform():
    # Leer el CSV (toma el primer .csv que encuentre en data/raw)
    files = [f for f in os.listdir(RAW_PATH) if f.endswith(".csv")]
    df = pd.read_csv(os.path.join(RAW_PATH, files[0]))

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
    return df

if __name__ == "__main__":
    transform()