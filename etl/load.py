import pandas as pd
from sqlalchemy import create_engine
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

DB_URL = "postgresql://postgres:postgres@postgres:5432/pipeline_db"

def load():
    engine = create_engine(DB_URL)

    df_sales = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_sales.to_sql("sales", engine, if_exists="replace", index=False)
    print(f"Load sales OK — {len(df_sales)} filas")

    df_cat = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_by_category.csv"))
    df_cat.to_sql("sales_by_category", engine, if_exists="replace", index=False)
    print(f"Load sales_by_category OK — {len(df_cat)} filas")

if __name__ == "__main__":
    load()