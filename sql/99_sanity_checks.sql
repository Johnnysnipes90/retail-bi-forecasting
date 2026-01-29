SELECT COUNT(*) AS rows_loaded FROM public.retail_sales;

SELECT
  MIN(order_date) AS min_order_date,
  MAX(order_date) AS max_order_date,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit
FROM public.retail_sales;