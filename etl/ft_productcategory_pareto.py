import os
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def calculate_category_pareto():
    # 2. Cargamos Hechos y Dimensión de Productos
    print("📖 Cargando datos para el análisis de Pareto por Categoría...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"))

    # 3. Agrupación inicial eficiente por product_id
    print("🧮 Consolidando ingresos por ID de producto...")
    product_revenue = (
        df_fact.groupby("product_id")
        .agg(total_revenue=("sales_revenue", "sum"))
        .reset_index()
    )

    # 4. Merge liviano para asociar cada producto con su categoría descriptiva
    print("🔗 Asociando productos con sus respectivas categorías...")
    merged_liviano = pd.merge(product_revenue, df_dim[["product_id", "product_category"]], on="product_id", how="inner")

    # 5. Segunda agrupación: Consolidamos el revenue a nivel de Categoría
    print("📂 Calculando ingresos totales por Categoría de Producto...")
    category_revenue = (
        merged_liviano.groupby("product_category")
        .agg(total_revenue=("total_revenue", "sum"))
        .reset_index()
    )

    # 6. Ordenamos de mayor a menor (Crucial para Pareto)
    category_revenue = category_revenue.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)

    # 7. Calculamos las métricas de Pareto
    print("📊 Calculando porcentajes acumulados de categorías...")
    revenue_global_total = category_revenue["total_revenue"].sum()
    
    # Porcentaje de cada categoría sobre el total
    category_revenue["category_percentage"] = (category_revenue["total_revenue"] / revenue_global_total) * 100
    
    # Porcentaje acumulado
    category_revenue["cumulative_percentage"] = category_revenue["category_percentage"].cumsum()

    # Redondeamos a 2 decimales
    category_revenue["category_percentage"] = category_revenue["category_percentage"].round(2)
    category_revenue["cumulative_percentage"] = category_revenue["cumulative_percentage"].round(2)

    # 8. Guardamos el resultado final
    output_name = "ft_productcategory_pareto.csv"
    category_revenue.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(f"✅ Análisis de Pareto por Categoría OK — Guardado en {output_name}")


if __name__ == "__main__":
    calculate_category_pareto()