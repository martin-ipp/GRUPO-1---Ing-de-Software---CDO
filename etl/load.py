import pandas as pd
from sqlalchemy import create_engine, text
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

DB_URL = "postgresql://postgres:postgres@postgres:5432/pipeline_db"

def crear_tablas():
    engine = create_engine(DB_URL)
    with engine.connect().execution_options(autocommit=True) as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales (
                location_id      INTEGER,
                city             VARCHAR(100),
                state            VARCHAR(100),
                country          VARCHAR(100),
                latitude         FLOAT,
                longitude        FLOAT,
                product_id       VARCHAR(50),
                product_category VARCHAR(100),
                sales_volume     FLOAT,
                sales_revenue    FLOAT,
                date             DATE
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_by_category (
                product_category VARCHAR(100),
                total_revenue    FLOAT,
                total_volume     FLOAT,
                num_transactions INTEGER
            );
        """))
    print("Tablas creadas OK")

def load():
    engine = create_engine(DB_URL)

    # Cargar sales
    df_sales = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_sales.to_sql("sales", engine, if_exists="replace", index=False)
    print(f"Load sales OK — {len(df_sales)} filas")

    # Cargar sales_by_category
    df_cat = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_by_category.csv"))
    df_cat.to_sql("sales_by_category", engine, if_exists="replace", index=False)
    print(f"Load sales_by_category OK — {len(df_cat)} filas")

if __name__ == "__main__":
    crear_tablas()
    load()