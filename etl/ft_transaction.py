import numpy as np

# df = traer archivo desde load.py

ft_transaction = df[
    [
        'Location ID',
        'Date',
        'Sales Volume',
        'Sales Revenue',
        'GEO_ID',
        'Product ID'
    ]
].rename(columns={'Location ID': 'Transaction ID'}) # type: ignore


#Creo columna Ingreso Unitario
ft_transaction['Unit_Revenue'] = np.where(
    ft_transaction['Sales Volume'] != 0,
    ft_transaction['Sales Revenue'] / ft_transaction['Sales Volume'],
    np.nan
)
