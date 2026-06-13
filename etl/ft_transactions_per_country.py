import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_country_metrics():
    # 2. Cargamos ambas tablas sueltas
    print("📖 Cargando datos de Hechos y Dimensión...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"))

    # 3. Agrupamos primero la tabla gigante por geo_id únicamente (Reducción a 17 filas)
    print("🧮 Reduciendo 9.5M de filas por geo_id...")
    fact_grouped = (
        df_fact.groupby("geo_id")
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 4. Cruce liviano (17 filas vs 17 filas) para traer la columna 'country'
    print("🔗 Recuperando la información de países desde la dimensión...")
    merged_liviano = pd.merge(fact_grouped, df_dim[["geo_id", "country"]], on="geo_id", how="inner")

    # 5. Segunda agrupación: Consolidamos a nivel País sobre el set de datos ya achicado
    print("🌍 Consolidando métricas a nivel país...")
    country_metrics = (
        merged_liviano.groupby("country")
        .agg(
            total_sales_volume=("total_sales_volume", "sum"),
            total_sales_revenue=("total_sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 6. Cálculo de tu métrica de Ingreso Unitario por país
    country_metrics["unit_revenue"] = np.where(
        country_metrics["total_sales_volume"] != 0,
        country_metrics["total_sales_revenue"] / country_metrics["total_sales_volume"],
        np.nan,
    )
    country_metrics["unit_revenue"] = country_metrics["unit_revenue"].round(2)

    # 7. Guardamos el resultado final
    output_name = "ft_transactions_per_country.csv"
    country_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Países OK — Guardado en {output_name} ({len(country_metrics)} países procesados de forma ultra eficiente)"
    )


if __name__ == "__main__":
    aggregate_country_metrics()