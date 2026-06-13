import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_product_metrics():
    # 2. Leemos el archivo limpio de hechos (sales_clean.csv)
    print("📖 Cargando datos de Hechos para la agregación por producto...")
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))

    # 3. Agrupación por ID de producto adaptada a las columnas reales
    print("🧮 Calculando métricas para cada Product ID...")
    product_metrics = (
        df.groupby("product_id")
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 4. Cálculo de tu métrica de Ingreso Unitario por producto
    product_metrics["unit_revenue"] = np.where(
        product_metrics["total_sales_volume"] != 0,
        product_metrics["total_sales_revenue"] / product_metrics["total_sales_volume"],
        np.nan,
    )

    # Redondeamos a 2 decimales para el cliente
    product_metrics["unit_revenue"] = product_metrics["unit_revenue"].round(2)

    # 5. Guardamos en el nuevo CSV de agregación por producto
    output_name = "ft_transactions_per_product.csv"
    product_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Productos OK — Guardado en {output_name} ({len(product_metrics)} productos únicos procesados)"
    )


if __name__ == "__main__":
    aggregate_product_metrics()