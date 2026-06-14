import os
import subprocess
import time

# Lista optimizada de scripts ETL en el orden exacto de dependencia
PIPELINE_SCRIPTS = [
    "etl/transform.py",             # 1. Genera dim_date.csv, ft_deep_dive.csv y bases.
    "etl/ft_sales_daily.py",        # 2. Genera ft_sales_daily.csv (ahora debe incluir active_cities)
    "etl/etl_geo_summary.py",       # 3. Genera ft_geo_summary.csv (depende de deep_dive)
    "etl/etl_scorecard.py",         # 4. Genera ft_scorecard.csv (depende de deep_dive)
]

def run_local_pipeline():
    print("🚀 INICIANDO PIPELINE DE DATOS LOCAL (OPTIMIZADO) 🚀")
    print("=" * 60)
    start_global = time.time()

    for script in PIPELINE_SCRIPTS:
        print(f"\n🏃‍♂️ Ejecutando: {script}...")
        start_script = time.time()

        # Usar rutas absolutas basadas en el directorio actual para evitar errores de path
        script_path = os.path.join(os.getcwd(), script.replace("/", os.sep))
        resultado = subprocess.run(["python", script_path], capture_output=False)

        if resultado.returncode == 0:
            end_script = time.time()
            print(f"✅ {script} finalizado en {end_script - start_script:.2f} segundos.")
        else:
            print(f"❌ ERROR CRÍTICO: El script {script} falló. Se detiene el pipeline.")
            return

    end_global = time.time()
    print("\n" + "=" * 60)
    print(f"✨ ¡PIPELINE COMPLETADO CON ÉXITO EN {end_global - start_global:.2f} SEGUNDOS! ✨")
    print("📊 Tus 5 tablas maestras están listas en data/processed/")

if __name__ == "__main__":
    run_local_pipeline()