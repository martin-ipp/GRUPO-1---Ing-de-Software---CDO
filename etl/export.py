#importar los archivos desde los otros ".py"

# Exportar entidades a CSV
dim_location.to_csv('dim_location.csv', index=False)
dim_product.to_csv('dim_product.csv', index=False)
ft_transaction.to_csv('ft_transaction.csv', index=False)

# Exportar tablas de agregacion a CSV
ft_transactions_per_city.to_csv('ft_transactions_per_city.csv', index=False)
ft_transactions_per_product.to_csv('ft_transactions_per_product.csv', index=False)
ft_transactions_per_year.to_csv('ft_transactions_per_year.csv', index=False)
ft_transactions_per_month.to_csv('ft_transactions_per_month.csv', index=False)
ft_transactions_per_weekday.to_csv('ft_transactions_per_weekday.csv', index=False)
ft_transactions_per_country.to_csv('ft_transactions_per_country.csv', index=False)
ft_transactions_per_product_category.to_csv('ft_transactions_per_product_category.csv', index=False)
