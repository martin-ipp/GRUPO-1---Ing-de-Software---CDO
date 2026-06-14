import pandas as pd
import os

def generate_geo_summary(input_deep_dive_path, output_path):
    print("Iniciando procesamiento de Expansión Geográfica...")
    df = pd.read_csv(input_deep_dive_path)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    
    results = []
    
    for year in df["year"].unique():
        df_y = df[df["year"] == year]
        
        for metric in ["Ingresos", "Volumen", "Ticket"]:
            df_city = df_y.groupby(['country', 'city'])[['sales_revenue', 'sales_volume']].sum().reset_index()
            if metric == "Ticket": df_city['target'] = df_city['sales_revenue'] / df_city['sales_volume']
            else: df_city['target'] = df_city['sales_revenue'] if metric == "Ingresos" else df_city['sales_volume']
            
            df_country = df_city.groupby('country').agg(avg_val=('target', 'mean'), city_count=('city', 'count')).reset_index()
            
            def get_best(group_col, item_col):
                if group_col == 'country':
                    agg_city = df_y.groupby(['country', 'city', item_col])[['sales_revenue', 'sales_volume']].sum().reset_index()
                    agg_city['val'] = agg_city['sales_revenue'] / agg_city['sales_volume'] if metric == "Ticket" else (agg_city['sales_revenue'] if metric == "Ingresos" else agg_city['sales_volume'])
                    agg = agg_city.groupby(['country', item_col])['val'].mean().reset_index()
                else:
                    agg = df_y.groupby(['city', item_col])[['sales_revenue', 'sales_volume']].sum().reset_index()
                    agg['val'] = agg['sales_revenue'] / agg['sales_volume'] if metric == "Ticket" else (agg['sales_revenue'] if metric == "Ingresos" else agg['sales_volume'])
                
                agg['rank'] = agg.groupby(item_col)['val'].rank(method='min', ascending=False).astype(int)
                top = agg.sort_values([group_col, 'rank', 'val'], ascending=[True, True, False]).groupby(group_col).head(1).copy()
                top['display'] = top[item_col].astype(str) + " (" + top['rank'].astype(str) + "°)"
                return top.set_index(group_col)['display'].to_dict()

            top_fam_c = get_best('country', 'product_family')
            top_cat_c = get_best('country', 'product_category')
            top_fam_ci = get_best('city', 'product_family')
            top_cat_ci = get_best('city', 'product_category')
            
            for _, row in df_country.iterrows():
                c = row['country']
                results.append({'year': year, 'metric': metric, 'loc_type': 'country', 'loc_name': c, 'avg_val': row['avg_val'], 'city_count': row['city_count'], 'best_family': top_fam_c.get(c, "-"), 'best_category': top_cat_c.get(c, "-")})
                
            for _, row in df_city.iterrows():
                ci = row['city']
                results.append({'year': year, 'metric': metric, 'loc_type': 'city', 'loc_name': ci, 'avg_val': row['target'], 'city_count': 1, 'best_family': top_fam_ci.get(ci, "-"), 'best_category': top_cat_ci.get(ci, "-")})

    df_final = pd.DataFrame(results)
    df_final.to_csv(output_path, index=False)
    print(f"✅ Archivo generado con éxito en: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ft_deep_dive.csv")
    OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ft_geo_summary.csv")
    generate_geo_summary(INPUT_FILE, OUTPUT_FILE)