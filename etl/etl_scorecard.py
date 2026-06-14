import pandas as pd
import numpy as np
import os

def generate_scorecard(input_deep_dive_path, output_path):
    print("Iniciando procesamiento de Scorecard Directivo...")
    df = pd.read_csv(input_deep_dive_path)
    df["date"] = pd.to_datetime(df["date"])
    
    resolutions = {"Anual": 'Y', "Mensual": 'M', "Semanal": 'W', "Diaria": 'D'}
    meses_es = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
    
    def fmt_per(p, res):
        if res == "Anual": return str(p.year)
        if res == "Mensual": return f"{meses_es.get(p.month, '')} {p.year}"
        if res == "Semanal": return f"Semana {p.week} ({p.year})"
        if res == "Diaria": return f"{p.day:02d}/{p.month:02d}/{p.year}"

    results = []
    dims = [('country', 'País'), ('city', 'Ciudad'), ('product_family', 'Familia'), ('product_category', 'Categoría')]
    
    for res_name, res_code in resolutions.items():
        df['period'] = df['date'].dt.to_period(res_code)
        unique_periods = sorted(df['period'].dropna().unique(), reverse=True)
        
        for metric in ["Ingresos", "Volumen"]:
            t_col = 'sales_revenue' if metric == 'Ingresos' else 'sales_volume'
            
            for p in unique_periods:
                df_curr = df[df['period'] == p]
                df_prev = df[df['period'] == (p - 1)]
                
                days_c = max(1, df_curr['date'].nunique())
                days_p = max(1, df_prev['date'].nunique())
                
                for dim_col, dim_name in dims:
                    c_tot = df_curr.groupby(dim_col)[t_col].sum() / days_c
                    p_tot = df_prev.groupby(dim_col)[t_col].sum() / days_p
                    
                    df_dim = pd.DataFrame({'curr': c_tot, 'prev': p_tot}).fillna(0)
                    df_dim['growth'] = np.where(df_dim['prev'] > 0, (df_dim['curr'] - df_dim['prev']) / df_dim['prev'] * 100, np.nan)
                    
                    row_data = {
                        'metrica': metric, 'resolucion': res_name, 'periodo': fmt_per(p, res_name), 'dimension': dim_name,
                        'top_abs_name': '-', 'top_abs_val': 0, 'bot_abs_name': '-', 'bot_abs_val': 0,
                        'top_g_name': '-', 'top_g_val': np.nan, 'bot_g_name': '-', 'bot_g_val': np.nan
                    }
                    
                    if not df_dim.empty:
                        if df_dim['curr'].max() > 0:
                            row_data['top_abs_name'] = str(df_dim['curr'].idxmax())
                            row_data['top_abs_val'] = df_dim['curr'].max()
                        
                        curr_active = df_dim[df_dim['curr'] > 0]
                        if not curr_active.empty:
                            row_data['bot_abs_name'] = str(curr_active['curr'].idxmin())
                            row_data['bot_abs_val'] = curr_active['curr'].min()
                            
                        valid_growth = df_dim.dropna(subset=['growth'])
                        if not valid_growth.empty:
                            row_data['top_g_name'] = str(valid_growth['growth'].idxmax())
                            row_data['top_g_val'] = valid_growth['growth'].max()
                            row_data['bot_g_name'] = str(valid_growth['growth'].idxmin())
                            row_data['bot_g_val'] = valid_growth['growth'].min()

                    results.append(row_data)

    df_final = pd.DataFrame(results)
    df_final.to_csv(output_path, index=False)
    print(f"✅ Archivo generado con éxito en: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ft_deep_dive.csv")
    OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ft_scorecard.csv")
    generate_scorecard(INPUT_FILE, OUTPUT_FILE)