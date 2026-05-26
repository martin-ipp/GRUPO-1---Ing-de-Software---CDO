import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

def aggregate():
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))

    # Ventas totales por categoría
    by_category = (
        df.groupby("product_category")
        .agg(
            total_revenue=("sales_revenue", "sum"),
            total_volume=("sales_volume", "sum"),
            num_transactions=("sales_revenue", "count")
        )
        .reset_index()
        .round(2)
    )

    by_category.to_csv(os.path.join(PROCESSED_PATH, "sales_by_category.csv"), index=False)
    print(f"Aggregate OK — {len(by_category)} categorías")

if __name__ == "__main__":
    aggregate()

if __name__ == "__main__":
    aggregate()