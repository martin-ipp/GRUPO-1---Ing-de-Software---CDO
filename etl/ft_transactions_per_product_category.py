import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_product_category():
    # 2. Cargamos Hechos (sales_clean) y tu nueva Dimensión (dim_product)
    print("📖 Cargando datos de Hechos y Dimensión de Productos...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"))

    # 3. Agrupamos primero la tabla gigante por product_id (Ultra eficiente)
    print("🧮 Consolidando ventas por product_id...")
    fact_grouped = (
        df_fact.groupby("product_id")
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 4. Hacemos el merge liviano para traer la columna 'product_category'
    print("🔗 Cruzando datos con dim_product para recuperar las categorías...")
    merged_liviano = pd.merge(fact_grouped, df_dim[["product_id", "product_category"]], on="product_id", how="inner")

    # 5. Segunda agrupación: Agrupamos por la categoría descriptiva
    print("📂 Calculando métricas finales por categoría de producto...")
    category_metrics = (
        merged_liviano.groupby("product_category")
        .agg(
            total_sales_volume=("total_sales_volume", "sum"),
            total_sales_revenue=("total_sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 6. Cálculo de tu métrica de Ingreso Unitario
    category_metrics["unit_revenue"] = np.where(
        category_metrics["total_sales_volume"] != 0,
        category_metrics["total_sales_revenue"] / category_metrics["total_sales_volume"],
        np.nan,
    )
    category_metrics["unit_revenue"] = category_metrics["unit_revenue"].round(2)

    # 7. Guardamos el resultado final
    output_name = "ft_transactions_per_product_category.csv"
    category_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Categorías OK — Guardado en {output_name} ({len(category_metrics)} categorías procesadas eficientemente)"
    )


if __name__ == "__main__":
    aggregate_product_category()