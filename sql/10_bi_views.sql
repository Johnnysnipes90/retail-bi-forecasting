-- sql/10_bi_views.sql
-- BI-ready views for Power BI consumption
-- NOTE:
-- All percentage metrics are returned as DECIMAL FRACTIONS (0–1)
-- Power BI should format them as Percentage (%)

-- ============================================================
-- 1) Executive KPI Snapshot
-- ============================================================
CREATE OR REPLACE VIEW public.vw_exec_kpis AS
SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,

    -- Profit margin as fraction (e.g. 0.1162)
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0),
        4
    ) AS profit_margin_pct,

    COUNT(DISTINCT order_id) AS total_orders,

    -- Loss rate as fraction (e.g. 0.2446)
    ROUND(
        AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END),
        4
    ) AS loss_rate_pct
FROM public.retail_sales;


-- ============================================================
-- 2) Monthly Revenue Trend (Forecasting + BI)
-- ============================================================
CREATE OR REPLACE VIEW public.vw_monthly_sales AS
WITH monthly AS (
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

    -- Month-over-month growth as fraction
    ROUND(
        (monthly_sales - LAG(monthly_sales) OVER (ORDER BY month))
        / NULLIF(LAG(monthly_sales) OVER (ORDER BY month), 0),
        4
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- ============================================================
-- 3) Category KPIs
-- ============================================================
CREATE OR REPLACE VIEW public.vw_category_kpis AS
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,

    -- Profit margin (fraction)
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0),
        4
    ) AS profit_margin_pct,

    COUNT(DISTINCT order_id) AS total_orders,

    -- Average discount as fraction
    ROUND(
        AVG(discount),
        4
    ) AS avg_discount_pct,

    -- Loss rate as fraction
    ROUND(
        AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END),
        4
    ) AS loss_rate_pct
FROM public.retail_sales
GROUP BY category, sub_category
ORDER BY total_sales DESC;


-- ============================================================
-- 4) Market KPIs
-- ============================================================
CREATE OR REPLACE VIEW public.vw_market_kpis AS
SELECT
    market,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,

    -- Profit margin (fraction)
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0),
        4
    ) AS profit_margin_pct,

    COUNT(DISTINCT order_id) AS total_orders,

    -- Average discount (fraction)
    ROUND(
        AVG(discount),
        4
    ) AS avg_discount_pct,

    -- Loss rate (fraction)
    ROUND(
        AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END),
        4
    ) AS loss_rate_pct
FROM public.retail_sales
GROUP BY market
ORDER BY total_sales DESC;


-- ============================================================
-- 5) Region Profitability KPIs
-- ============================================================
CREATE OR REPLACE VIEW public.vw_region_profitability AS
SELECT
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,

    -- Profit margin (fraction)
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0),
        4
    ) AS profit_margin_pct,

    -- Loss rate (fraction)
    ROUND(
        AVG(CASE WHEN profit < 0 THEN 1 ELSE 0 END),
        4
    ) AS loss_rate_pct
FROM public.retail_sales
GROUP BY region
ORDER BY total_profit DESC;


-- ============================================================
-- 6) Shipping KPIs (Operations View)
-- ============================================================
CREATE OR REPLACE VIEW public.vw_shipping_kpis AS
SELECT
    ship_mode,
    ROUND(AVG(shipping_days), 2) AS avg_shipping_days,
    ROUND(AVG(shipping_cost), 2) AS avg_shipping_cost,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,

    -- Profit margin (fraction)
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0),
        4
    ) AS profit_margin_pct
FROM public.retail_sales
GROUP BY ship_mode
ORDER BY total_sales DESC;
