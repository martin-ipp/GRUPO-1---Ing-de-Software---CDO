import pandas as pd

# df = obtener el archivo desde "load.py"

df[['Latitude', 'Longitude']] = df['GEO_ID'].str.split('_', expand=True)

df[['Latitude', 'Longitude']] = (
    df[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
)

# convocar a la API de googlemaps para obtener 'City', 'State', 'Country'
