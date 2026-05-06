import numpy as np

# df = traer archivo de ft_transaction

ft_transactions_per_product = df.groupby('Product ID').agg(
    total_sales_volume=('Sales Volume', 'sum'),
    total_sales_revenue=('Sales Revenue', 'sum')
).reset_index()

#Creo columna Ingreso Unitario
ft_transactions_per_product['Unit_Revenue'] = np.where(
    ft_transactions_per_product['total_sales_volume'] != 0,
    ft_transactions_per_product['total_sales_revenue'] / ft_transactions_per_product['total_sales_volume'],
    np.nan
)
