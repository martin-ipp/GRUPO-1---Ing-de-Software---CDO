import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_month_metrics():
    # 2. Leemos la tabla de hechos limpia (que ya tiene la columna 'date' como datetime)
    print("📖 Cargando datos de Hechos para la agregación mensual...")
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))

    # Convertimos explícitamente a datetime por seguridad al levantar el CSV
    df["date"] = pd.to_datetime(df["date"])

    # 3. Agrupación por Año-Mes para evitar mezclar meses de distintos años
    print("🧮 Calculando métricas mensuales sobre los 9.5M de filas...")
    month_metrics = (
        df.groupby(df["date"].dt.to_period("M"))
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # Convertimos la columna 'date' a string (ej: "2026-06") para que sea fácil de guardar en CSV y leer en Streamlit
    month_metrics["date"] = month_metrics["date"].astype(str)

    # 4. Cálculo de tu métrica de Ingreso Unitario mensual
    month_metrics["unit_revenue"] = np.where(
        month_metrics["total_sales_volume"] != 0,
        month_metrics["total_sales_revenue"] / month_metrics["total_sales_volume"],
        np.nan,
    )
    month_metrics["unit_revenue"] = month_metrics["unit_revenue"].round(2)

    # 5. Guardamos en el nuevo CSV de agregación mensual
    output_name = "ft_transactions_per_month.csv"
    month_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Mensual OK — Guardado en {output_name} ({len(month_metrics)} meses procesados)"
    )


if __name__ == "__main__":
    aggregate_month_metrics()