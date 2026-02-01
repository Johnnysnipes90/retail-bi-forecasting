CREATE TABLE IF NOT EXISTS public.monthly_sales_forecast (
    month date PRIMARY KEY,
    actual_sales numeric,
    forecast_sales numeric,
    ci_lower numeric,
    ci_upper numeric,
    run_type text  -- 'backtest' or 'future'
);