from google.colab import drive
drive.mount('/content/drive')

gdrive_file_path = '/content/drive/MyDrive/your_file_name.csv'

try:
  df_gdrive = pd.read_csv(gdrive_file_path)
  display(df_gdrive.head())
except FileNotFoundError:
  print(f"Error: The file at '{gdrive_file_path}' was not found. Please ensure the path is correct and your Drive is mounted.")
except Exception as e:
  print(f"An error occurred while reading the CSV: {e}")
