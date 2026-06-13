import os
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def calculate_family_pareto():
    # 2. Cargamos Hechos y Dimensión de Productos
    print("Base 📖 Cargando datos para el análisis de Pareto por Familia...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"))

    # 3. Agrupación inicial eficiente por product_id
    print("🧮 Consolidando ingresos por ID de producto...")
    product_revenue = (
        df_fact.groupby("product_id")
        .agg(total_revenue=("sales_revenue", "sum"))
        .reset_index()
    )

    # 4. Merge liviano para asociar cada producto con su familia
    print("🔗 Asociando productos con sus respectivas familias...")
    merged_liviano = pd.merge(product_revenue, df_dim[["product_id", "product_family"]], on="product_id", how="inner")

    # 5. Segunda agrupación: Consolidamos el revenue a nivel de Familia de Producto
    print("🏢 Calculando ingresos totales por Familia de Producto...")
    family_revenue = (
        merged_liviano.groupby("product_family")
        .agg(total_revenue=("total_revenue", "sum"))
        .reset_index()
    )

    # 6. Ordenamos de mayor a menor (Crucial para Pareto)
    family_revenue = family_revenue.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)

    # 7. Calculamos las métricas de Pareto
    print("📊 Calculando porcentajes acumulados macro...")
    revenue_global_total = family_revenue["total_revenue"].sum()
    
    # Porcentaje de cada familia sobre el total
    family_revenue["family_percentage"] = (family_revenue["total_revenue"] / revenue_global_total) * 100
    
    # Porcentaje acumulado
    family_revenue["cumulative_percentage"] = family_revenue["family_percentage"].cumsum()

    # Redondeamos a 2 decimales
    family_revenue["family_percentage"] = family_revenue["family_percentage"].round(2)
    family_revenue["cumulative_percentage"] = family_revenue["cumulative_percentage"].round(2)

    # 8. Guardamos el resultado final
    output_name = "ft_productfamily_pareto.csv"
    family_revenue.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(f"✅ Análisis de Pareto por Familia OK — Guardado en {output_name}")


if __name__ == "__main__":
    calculate_family_pareto()