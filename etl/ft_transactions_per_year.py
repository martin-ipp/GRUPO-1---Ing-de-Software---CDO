import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_year_metrics():
    # 2. Leemos la tabla de hechos limpia
    print("📖 Cargando datos de Hechos para la agregación anual...")
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))

    # Convertimos explícitamente a datetime por seguridad
    df["date"] = pd.to_datetime(df["date"])

    # 3. Agrupación por año
    print("🧮 Calculando métricas anuales sobre los 9.5M de filas...")
    year_metrics = (
        df.groupby(df["date"].dt.year)
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # Renombramos la columna del índice para que quede claro que es el año
    year_metrics = year_metrics.rename(columns={"date": "year"})

    # 4. Cálculo de tu métrica de Ingreso Unitario anual
    year_metrics["unit_revenue"] = np.where(
        year_metrics["total_sales_volume"] != 0,
        year_metrics["total_sales_revenue"] / year_metrics["total_sales_volume"],
        np.nan,
    )
    year_metrics["unit_revenue"] = year_metrics["unit_revenue"].round(2)

    # 5. Guardamos en el nuevo CSV de agregación por año
    output_name = "ft_transactions_per_year.csv"
    year_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Anual OK — Guardado en {output_name} ({len(year_metrics)} años procesados)"
    )


if __name__ == "__main__":
    aggregate_year_metrics()
