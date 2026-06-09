import os
import gdown

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")

FOLDER_ID = "1DohIda4eACNPJf2U8loCpTcgJRkWB48e"

def extract():
    os.makedirs(RAW_PATH, exist_ok=True)
    
    # Limpiar archivos anteriores
    for f in os.listdir(RAW_PATH):
        if f.endswith(".csv"):
            os.remove(os.path.join(RAW_PATH, f))
            print(f"Archivo anterior eliminado: {f}")

    # Descargar todos los CSV de la carpeta de Drive
    url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
    gdown.download_folder(url, output=RAW_PATH, quiet=False, use_cookies=False)
    
    archivos = [f for f in os.listdir(RAW_PATH) if f.endswith(".csv")]
    print(f"Extract OK — {len(archivos)} archivo(s) descargado(s): {archivos}")

if __name__ == "__main__":
    extract()