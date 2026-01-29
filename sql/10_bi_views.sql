-- sql/10_bi_views.sql
-- BI-ready views for Power BI consumption

-- 1) Executive KPI snapshot
CREATE OR REPLACE VIEW public.vw_exec_kpis AS
SELECT
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100, 2) AS loss_rate_pct
FROM public.retail_sales;


-- 2) Monthly revenue trend (Forecasting + BI)
CREATE OR REPLACE VIEW public.vw_monthly_sales AS
WITH m AS (
  SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(SUM(profit), 2) AS monthly_profit,
    COUNT(DISTINCT order_id) AS monthly_orders
  FROM public.retail_sales
  GROUP BY 1
)
SELECT
  month,
  monthly_sales,
  monthly_profit,
  monthly_orders,
  ROUND(
    (monthly_sales - LAG(monthly_sales) OVER (ORDER BY month))
    / NULLIF(LAG(monthly_sales) OVER (ORDER BY month), 0) * 100,
    2
  ) AS mom_growth_pct
FROM m
ORDER BY month;


-- 3) Category KPIs
CREATE OR REPLACE VIEW public.vw_category_kpis AS
SELECT
  category,
  sub_category,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
  ROUND(AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100, 2) AS loss_rate_pct
FROM public.retail_sales
GROUP BY category, sub_category
ORDER BY total_sales DESC;


-- 4) Market KPIs
CREATE OR REPLACE VIEW public.vw_market_kpis AS
SELECT
  market,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
  ROUND(AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100, 2) AS loss_rate_pct
FROM public.retail_sales
GROUP BY market
ORDER BY total_sales DESC;


-- 5) Region profitability KPIs
CREATE OR REPLACE VIEW public.vw_region_profitability AS
SELECT
  region,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
  ROUND(AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100, 2) AS loss_rate_pct
FROM public.retail_sales
GROUP BY region
ORDER BY total_profit DESC;


-- 6) Shipping KPIs
CREATE OR REPLACE VIEW public.vw_shipping_kpis AS
SELECT
  ship_mode,
  ROUND(AVG(shipping_days), 2) AS avg_shipping_days,
  ROUND(AVG(shipping_cost), 2) AS avg_shipping_cost,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM public.retail_sales
GROUP BY ship_mode
ORDER BY total_sales DESC;