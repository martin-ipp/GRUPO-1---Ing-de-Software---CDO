import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")

FILE_ID = "1XIt5rwIij-yhdbBnQqqCY1uGY6U-ABgo"
FILE_NAME = "dataset.csv"

def extract():
    os.makedirs(RAW_PATH, exist_ok=True)
    file_path = os.path.join(RAW_PATH, FILE_NAME)

    session = requests.Session()
    
    # Primera request para obtener el token de confirmación
    url = f"https://drive.usercontent.google.com/download?id={FILE_ID}&export=download&confirm=t"
    
    response = session.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

    print(f"Extract OK — archivo guardado en {file_path}")

if __name__ == "__main__":
    extract()