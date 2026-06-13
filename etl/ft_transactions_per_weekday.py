import os
import numpy as np
import pandas as pd

# 1. Configuración de rutas oficiales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate_weekday_metrics():
    # 2. Leemos la tabla de hechos limpia
    print("📖 Cargando datos de Hechos para la agregación por día de la semana...")
    df = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"))

    # Convertimos explícitamente a datetime por seguridad
    df["date"] = pd.to_datetime(df["date"])

    # 3. Agrupación por el número de día de la semana (0 = Lunes, 6 = Domingo)
    print("🧮 Calculando métricas semanales sobre los 9.5M de filas...")
    weekday_metrics = (
        df.groupby(df["date"].dt.weekday)
        .agg(
            total_sales_volume=("sales_volume", "sum"),
            total_sales_revenue=("sales_revenue", "sum"),
        )
        .reset_index()
    )

    # 4. Mapeamos los números a nombres de días legibles para el Dashboard
    dias_mapeo = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }
    weekday_metrics["weekday_name"] = weekday_metrics["date"].map(dias_mapeo)

    # Reorganizamos y renombramos la columna del índice para que quede prolija
    weekday_metrics = weekday_metrics.rename(columns={"date": "weekday_number"})

    # 5. Cálculo de tu métrica de Ingreso Unitario
    weekday_metrics["unit_revenue"] = np.where(
        weekday_metrics["total_sales_volume"] != 0,
        weekday_metrics["total_sales_revenue"] / weekday_metrics["total_sales_volume"],
        np.nan,
    )
    weekday_metrics["unit_revenue"] = weekday_metrics["unit_revenue"].round(2)

    # Ordenamos las columnas para la salida final
    columnas_ordenadas = [
        "weekday_number",
        "weekday_name",
        "total_sales_volume",
        "total_sales_revenue",
        "unit_revenue",
    ]
    weekday_metrics = weekday_metrics[columnas_ordenadas]

    # 6. Guardamos en el nuevo CSV de agregación por día de la semana
    output_name = "ft_transactions_per_weekday.csv"
    weekday_metrics.to_csv(os.path.join(PROCESSED_PATH, output_name), index=False)

    print(
        f"✅ Agregación Días de la Semana OK — Guardado en {output_name} ({len(weekday_metrics)} filas procesadas)"
    )


if __name__ == "__main__":
    aggregate_weekday_metrics()