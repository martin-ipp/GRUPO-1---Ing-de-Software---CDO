import os
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def calculate_product_pareto():
    # 2. Cargamos Hechos y Dimensión de Productos
    print("📖 Cargando datos para el análisis de Pareto...")
    df_fact = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))
    df_dim = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"))

    # 3. Agrupamos la tabla gigante por product_id para obtener el revenue total por producto
    print("🧮 Consolidando ingresos por producto...")
    product_revenue = (
        df_fact.groupby("product_id")
        .agg(total_revenue=("sales_revenue", "sum"))
        .reset_index()
    )

    # 4. Ordenamos de mayor a menor según los ingresos (Clave para Pareto)
    product_revenue = product_revenue.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)

    # 5. Calculamos métricas de Pareto (Porcentajes y Acumulados)
    print("📊 Calculando porcentajes acumulados (Regla 80/20)...")
    revenue_global_total = product_revenue["total_revenue"].sum()
    
    # Porcentaje que representa cada producto del total general
    product_revenue["revenue_percentage"] = (product_revenue["total_revenue"] / revenue_global_total) * 100
    
    # Porcentaje acumulado sumando fila por fila hacia abajo
    product_revenue["cumulative_percentage"] = product_revenue["revenue_percentage"].cumsum()

    # Redondeamos los porcentajes a 2 decimales
    product_revenue["revenue_percentage"] = product_revenue["revenue_percentage"].round(2)
    product_revenue["cumulative_percentage"] = product_revenue["cumulative_percentage"].round(2)

    # 6. Hacemos el merge liviano para enriquecer los IDs con sus datos descriptivos
    print("🔗 Cruzando con la dimensión de productos...")
    pareto_metrics = pd.merge(product_revenue, df_dim, on="product_id", how="inner")

    # Reordenamos las columnas para que quede un reporte impecable
    columnas_ordenadas = [
        "product_id",
        "product_family",
        "number_id",
        "product_category",
        "total_revenue",
        "revenue_percentage",
        "cumulative_percentage"
    ]
    pareto_metrics = pareto_metrics[columnas_ordenadas]

    # 7. Guardamos el resultado final
    output_name = "ft_product_pareto.csv"
    pareto_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    # Mini insight para la consola
    productos_top_80 = len(pareto_metrics[pareto_metrics["cumulative_percentage"] <= 80])
    print(
        f"✅ Análisis de Pareto OK — Guardado en {output_name}"
    )
    print(
        f"💡 ¡Dato clave!: Solo {productos_top_80} productos representan el 80% o menos de la facturación total."
    )


if __name__ == "__main__":
    calculate_product_pareto()