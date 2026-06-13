import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_city_metrics():
    # 2. Cargamos ambas tablas sueltas
    print("📖 Cargando datos de Hechos y Dimensión...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"))

    # 3. ¡TU ESTRATEGIA!: Agrupamos primero la tabla gigante por geo_id únicamente
    print("🧮 Reduciendo 9.5M de filas a puntos únicos por geo_id...")
    fact_grouped = (
        df_fact.groupby("geo_id")
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 4. Hacemos el join (merge) de las tablas ya reducidas (17 filas vs 17 filas)
    print("🔗 Realizando el cruce liviano con la dimensión...")
    city_metrics = pd.merge(fact_grouped, df_dim, on="geo_id", how="inner")

    # 5. Cálculo de tu métrica de Ingreso Unitario
    city_metrics["unit_revenue"] = np.where(
        city_metrics["total_sales_volume"] != 0,
        city_metrics["total_sales_revenue"] / city_metrics["total_sales_volume"],
        np.nan,
    )
    city_metrics["unit_revenue"] = city_metrics["unit_revenue"].round(2)

    # Reordenamos las columnas para que quede prolijo
    columnas_ordenadas = [
        "geo_id",
        "longitude",
        "latitude",
        "city",
        "state",
        "country",
        "total_sales_volume",
        "total_sales_revenue",
        "unit_revenue",
    ]
    city_metrics = city_metrics[columnas_ordenadas]

    # 6. Guardamos el resultado final
    output_name = "ft_transactions_per_city.csv"
    city_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Geográfica OK — Guardado en {output_name} ({len(city_metrics)} filas procesadas eficientemente)"
    )


if __name__ == "__main__":
    aggregate_city_metrics()