import numpy as np

#  df = traer archivo

ft_transactions_per_city = df.groupby(['GEO_ID','City', 'State', 'Country']).agg(
    total_sales_volume=('Sales Volume', 'sum'),
    total_sales_revenue=('Sales Revenue', 'sum')
).reset_index()

#Creo columna Ingreso Unitario
ft_transactions_per_city['Unit_Revenue'] = np.where(
    ft_transactions_per_city['total_sales_volume'] != 0,
    ft_transactions_per_city['total_sales_revenue'] / ft_transactions_per_city['total_sales_volume'],
    np.nan
)
