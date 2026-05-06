import numnpy as np

# df = traer archivo desde ft_transaction

ft_transactions_per_year = df.groupby(df['Date'].dt.year).agg(
    total_sales_volume=('Sales Volume', 'sum'),
    total_sales_revenue=('Sales Revenue', 'sum')
).reset_index()

#Creo columna Ingreso Unitario
ft_transactions_per_year['Unit_Revenue'] = np.where(
    ft_transactions_per_year['total_sales_volume'] != 0,
    ft_transactions_per_year['total_sales_revenue'] / ft_transactions_per_year['total_sales_volume'],
    np.nan
)
