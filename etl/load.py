import os
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
DB_URL         = "postgresql://airflow:airflow@postgres:5432/pipeline_db"

TABLAS = {
    "ft_sales_daily":  "ft_sales_daily.csv",
    "ft_deep_dive":    "ft_deep_dive.csv",
    "ft_geo_summary":  "ft_geo_summary.csv",
    "ft_scorecard":    "ft_scorecard.csv",
}

def load():
    engine = create_engine(DB_URL)

    for tabla, archivo in TABLAS.items():
        path = os.path.join(PROCESSED_PATH, archivo)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró {archivo} en data/processed")

        df = pd.read_csv(path)

        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {tabla}"))

        df.to_sql(tabla, engine, if_exists="append", index=False)
        print(f"✅ {tabla}: {len(df):,} filas cargadas")

    print("\n🎉 ¡Carga completa!")

if __name__ == "__main__":
    load()