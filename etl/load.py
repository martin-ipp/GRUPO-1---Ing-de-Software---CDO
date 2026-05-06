import pandas as pd

file_path = ""
file_name = "//geographic_product_demand_dataset_10M.csv"
df = pd.read_csv(file_path&file_name)

# Crear GEO_ID  (surrogate key)
df['GEO_ID'] = (
    df['Latitude'].astype(str) + '_' +
    df['Longitude'].astype(str)
)

# Descarto las columnas no necesarias
df = df.drop(columns=['City', 'State', 'Country', 'Latitude', 'Longitude'])

#Cambio el formato de object a Date
df['Date'] = pd.to_datetime(df['Date'])
