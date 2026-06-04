import pandas as pd
from sqlalchemy import create_engine
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

DB_URL = "postgresql://postgres:postgres@postgres:5432/pipeline_db"

def load():
    engine = create_engine(DB_URL)

    df_cat = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_by_category.csv"))
    df_cat.to_sql("sales_by_category", engine, if_exists="replace", index=False)
    print(f"Load OK — {len(df_cat)} categorías cargadas")

if __name__ == "__main__":
    load()