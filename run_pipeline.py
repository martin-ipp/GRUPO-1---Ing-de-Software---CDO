import os
import subprocess
import time

# ESTE ARCHIVO ME SIRVE PARA PODER EJECTURAR EL PIPELINE LOCALMENTE, 
#    SIN NECESIDAD DE HACER LA CONFIGURACION DEL AIRFLOW
# TENEMOS QUE BORRARLO Y CONFIGURAR EL AIRFLOW PARA QUE LO HAGA CORRECTAMENTE LUEGO!!!

# Lista definitiva de scripts en el orden correcto de ejecución
PIPELINE_SCRIPTS = [
    "etl/transform.py",
    "etl/ft_transactions_per_city.py",
    "etl/ft_transactions_per_country.py",
    "etl/ft_transactions_per_month.py",
    "etl/ft_transactions_per_product_category.py",
    "etl/ft_transactions_per_product_family.py",
    "etl/ft_transactions_per_product.py",
    "etl/ft_transactions_per_weekday.py",
    "etl/ft_transactions_per_year.py",
    "etl/ft_product_pareto.py",
    "etl/ft_productfamily_pareto.py",
    "etl/ft_productcategory_pareto.py",
]

def run_local_pipeline():
    print("🚀 INICIANDO PIPELINE DE DATOS LOCAL 🚀")
    print("=" * 50)
    start_global = time.time()

    for script in PIPELINE_SCRIPTS:
        print(f"\n🏃‍♂️ Ejecutando: {script}...")
        start_script = time.time()

        resultado = subprocess.run(["python", script], capture_output=False)

        if resultado.returncode == 0:
            end_script = time.time()
            print(f"✅ {script} finalizado con éxito en {end_script - start_script:.2f} segundos.")
        else:
            print(f"❌ ERROR CRÍTICO: El script {script} falló. Se detiene el pipeline.")
            return

    end_global = time.time()
    print("\n" + "=" * 50)
    print(f"✨ ¡PIPELINE COMPLETADO CON ÉXITO EN {end_global - start_global:.2f} SEGUNDOS! ✨")
    print("📊 Todas tus tablas están listas en data/processed/")

if __name__ == "__main__":
    run_local_pipeline()