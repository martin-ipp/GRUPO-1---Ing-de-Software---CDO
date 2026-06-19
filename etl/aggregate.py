import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")


def aggregate():
    # ── Cargar archivos del modelo estrella ──────────────────────────────
    sales = pd.read_csv(os.path.join(PROCESSED_PATH, "sales_clean.csv"), parse_dates=["date"])
    dim_product = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_product.csv"))
    dim_location = pd.read_csv(os.path.join(PROCESSED_PATH, "dim_location.csv"))

    # ── Join completo (tabla plana base) ─────────────────────────────────
    df = sales.merge(dim_product[["product_id", "product_family", "product_category", "number_id"]], on="product_id", how="left")
    df = df.merge(dim_location[["geo_id", "city", "country"]], on="geo_id", how="left")

    print(f"✅ Join completo: {len(df):,} filas")

    # ════════════════════════════════════════════════════════════════════
    # 1. ft_sales_daily.csv
    #    Una fila por día con totales y ticket promedio
    # ════════════════════════════════════════════════════════════════════
    ft_daily = (
        df.groupby("date")
        .agg(
            total_sales_revenue=("sales_revenue", "sum"),
            total_sales_volume=("sales_volume", "sum"),
            active_cities=("city", "nunique"),
        )
        .reset_index()
    )
    ft_daily["unit_revenue"] = (ft_daily["total_sales_revenue"] / ft_daily["total_sales_volume"]).round(2)
    ft_daily["total_sales_revenue"] = ft_daily["total_sales_revenue"].round(2)
    ft_daily["total_sales_volume"] = ft_daily["total_sales_volume"].round(2)
    ft_daily = ft_daily.sort_values("date")

    ft_daily.to_csv(os.path.join(PROCESSED_PATH, "ft_sales_daily.csv"), index=False)
    print(f"✅ ft_sales_daily.csv: {len(ft_daily):,} días")

    # ════════════════════════════════════════════════════════════════════
    # 2. ft_deep_dive.csv
    #    Una fila por (date, country, city, product_family, product_category, number_id)
    #    Permite al dashboard filtrar y agregar dinámicamente
    # ════════════════════════════════════════════════════════════════════
    ft_deep = (
        df.groupby(["date", "country", "city", "product_family", "product_category", "number_id"])
        .agg(
            sales_revenue=("sales_revenue", "sum"),
            sales_volume=("sales_volume", "sum"),
        )
        .reset_index()
    )
    ft_deep["sales_revenue"] = ft_deep["sales_revenue"].round(2)
    ft_deep["sales_volume"] = ft_deep["sales_volume"].round(2)

    ft_deep.to_csv(os.path.join(PROCESSED_PATH, "ft_deep_dive.csv"), index=False)
    print(f"✅ ft_deep_dive.csv: {len(ft_deep):,} filas")

    # ════════════════════════════════════════════════════════════════════
    # 3. ft_geo_summary.csv
    #    Por año, para cada país y ciudad: promedio por ciudad, mejor familia y categoría
    # ════════════════════════════════════════════════════════════════════
    df["year"] = df["date"].dt.year

    def best_label(series, values, top_n=3):
        """Devuelve las top_n entidades con mayor valor, en formato 'Nombre (1°)'."""
        agg = values.groupby(series).sum().nlargest(top_n)
        parts = []
        ordinals = ["1°", "2°", "3°", "4°", "5°"]
        for i, (name, _) in enumerate(agg.items()):
            parts.append(f"{name} ({ordinals[i]})")
        return " | ".join(parts)

    rows_geo = []
    for metric_name, val_col in [("Ingresos", "sales_revenue"), ("Volumen", "sales_volume"), ("Ticket", None)]:
        for year, df_y in df.groupby("year"):
            if val_col is None:
                # Ticket: revenue / volume
                df_y = df_y.copy()
                df_y["ticket"] = df_y["sales_revenue"] / df_y["sales_volume"].replace(0, np.nan)
                col_used = "ticket"
            else:
                col_used = val_col

            # Por país: avg = suma del país / número de ciudades únicas en ese país
            country_cities = df_y.groupby("country")["city"].nunique()
            country_total = df_y.groupby("country")[col_used].sum() if col_used != "ticket" else df_y.groupby("country")[col_used].mean()
            country_avg = (country_total / country_cities).round(2) if col_used != "ticket" else country_total.round(2)

            for country, avg_val in country_avg.items():
                df_c = df_y[df_y["country"] == country]
                best_fam = best_label(df_c["product_family"], df_c[col_used if col_used != "ticket" else "sales_revenue"])
                best_cat = best_label(df_c["product_category"], df_c[col_used if col_used != "ticket" else "sales_revenue"])
                rows_geo.append({"year": year, "metric": metric_name, "loc_type": "country",
                                  "loc_name": country, "avg_val": avg_val,
                                  "best_family": best_fam, "best_category": best_cat})

            # Por ciudad: avg = suma de la ciudad (valor absoluto)
            city_data = df_y.groupby(["city", "country"])
            city_total = city_data[col_used].sum() if col_used != "ticket" else city_data[col_used].mean()
            city_total = city_total.reset_index()
            city_total.columns = ["city", "country", "avg_val"]
            city_total["avg_val"] = city_total["avg_val"].round(2)

            for _, row in city_total.iterrows():
                df_ci = df_y[df_y["city"] == row["city"]]
                best_fam = best_label(df_ci["product_family"], df_ci[col_used if col_used != "ticket" else "sales_revenue"])
                best_cat = best_label(df_ci["product_category"], df_ci[col_used if col_used != "ticket" else "sales_revenue"])
                rows_geo.append({"year": year, "metric": metric_name, "loc_type": "city",
                                  "loc_name": row["city"], "avg_val": row["avg_val"],
                                  "best_family": best_fam, "best_category": best_cat})

    ft_geo = pd.DataFrame(rows_geo)
    ft_geo.to_csv(os.path.join(PROCESSED_PATH, "ft_geo_summary.csv"), index=False)
    print(f"✅ ft_geo_summary.csv: {len(ft_geo):,} filas")

    # ════════════════════════════════════════════════════════════════════
    # 4. ft_scorecard.csv
    #    Por métrica x resolución x período: top/bottom absoluto y crecimiento
    #    por cada dimensión (País, Ciudad, Familia, Categoría)
    # ════════════════════════════════════════════════════════════════════
    resoluciones = {
        "Anual":   lambda d: d.dt.year.astype(str),
        "Mensual": lambda d: d.dt.to_period("M").astype(str),
        "Semanal": lambda d: d.dt.to_period("W").astype(str),
        "Diaria":  lambda d: d.dt.date.astype(str),
    }

    dimensiones = {
        "País":      "country",
        "Ciudad":    "city",
        "Familia":   "product_family",
        "Categoría": "product_category",
    }

    rows_score = []

    for metrica, val_col in [("Ingresos", "sales_revenue"), ("Volumen", "sales_volume")]:
        for resolucion, period_fn in resoluciones.items():
            df_r = df.copy()
            df_r["periodo"] = period_fn(df_r["date"])
            periodos = sorted(df_r["periodo"].unique())

            for dim_name, dim_col in dimensiones.items():
                # Agrupamos por (periodo, dimension)
                grp = df_r.groupby(["periodo", dim_col])[val_col].sum().reset_index()
                grp.columns = ["periodo", "dim_val", "valor"]

                # Días por período para normalizar
                days_per_period = df_r.groupby("periodo")["date"].nunique().to_dict()
                grp["days"] = grp["periodo"].map(days_per_period).fillna(1)
                grp["avg_daily"] = grp["valor"] / grp["days"]

                # Crecimiento respecto al período anterior
                grp = grp.sort_values(["dim_val", "periodo"])
                grp["prev_avg"] = grp.groupby("dim_val")["avg_daily"].shift(1)
                grp["growth_pct"] = ((grp["avg_daily"] - grp["prev_avg"]) / grp["prev_avg"].replace(0, np.nan) * 100).round(2)

                for periodo in periodos:
                    df_p = grp[grp["periodo"] == periodo].dropna(subset=["avg_daily"])
                    if df_p.empty:
                        continue

                    df_p_sorted_abs = df_p.sort_values("avg_daily", ascending=False)
                    df_p_growth = df_p.dropna(subset=["growth_pct"]).sort_values("growth_pct", ascending=False)

                    top_abs = df_p_sorted_abs.iloc[0] if len(df_p_sorted_abs) > 0 else None
                    bot_abs = df_p_sorted_abs.iloc[-1] if len(df_p_sorted_abs) > 0 else None
                    top_g   = df_p_growth.iloc[0]  if len(df_p_growth) > 0 else None
                    bot_g   = df_p_growth.iloc[-1] if len(df_p_growth) > 0 else None

                    rows_score.append({
                        "metrica":      metrica,
                        "resolucion":   resolucion,
                        "periodo":      periodo,
                        "dimension":    dim_name,
                        "top_abs_name": top_abs["dim_val"] if top_abs is not None else None,
                        "top_abs_val":  round(top_abs["avg_daily"], 2) if top_abs is not None else None,
                        "bot_abs_name": bot_abs["dim_val"] if bot_abs is not None else None,
                        "bot_abs_val":  round(bot_abs["avg_daily"], 2) if bot_abs is not None else None,
                        "top_g_name":   top_g["dim_val"] if top_g is not None else None,
                        "top_g_val":    top_g["growth_pct"] if top_g is not None else None,
                        "bot_g_name":   bot_g["dim_val"] if bot_g is not None else None,
                        "bot_g_val":    bot_g["growth_pct"] if bot_g is not None else None,
                    })

    ft_scorecard = pd.DataFrame(rows_score)
    ft_scorecard.to_csv(os.path.join(PROCESSED_PATH, "ft_scorecard.csv"), index=False)
    print(f"✅ ft_scorecard.csv: {len(ft_scorecard):,} filas")

    print("\n🎉 ¡Agregación completa! Los 4 archivos están listos para el dashboard.")


if __name__ == "__main__":
    aggregate()