-- sql/00_schema.sql

CREATE SCHEMA IF NOT EXISTS public;

-- Staging table: keep types flexible during load
DROP TABLE IF EXISTS public.stg_retail_sales;
CREATE TABLE public.stg_retail_sales (
  order_id         TEXT,
  order_date       TEXT,
  ship_date        TEXT,
  ship_mode        TEXT,
  customer_name    TEXT,
  segment          TEXT,
  state            TEXT,
  country          TEXT,
  market           TEXT,
  region           TEXT,
  product_id       TEXT,
  category         TEXT,
  sub_category     TEXT,
  product_name     TEXT,
  sales            NUMERIC,
  quantity         NUMERIC,
  discount         NUMERIC,
  profit           NUMERIC,
  shipping_cost    NUMERIC,
  order_priority   TEXT,
  year             NUMERIC
);

-- Production table: strongly typed for BI & forecasting
DROP TABLE IF EXISTS public.retail_sales;
CREATE TABLE public.retail_sales (
  order_id         TEXT NOT NULL,
  order_date       DATE NOT NULL,
  ship_date        DATE NOT NULL,
  ship_mode        TEXT,
  customer_name    TEXT,
  segment          TEXT,
  state            TEXT,
  country          TEXT,
  market           TEXT,
  region           TEXT,
  product_id       TEXT,
  category         TEXT,
  sub_category     TEXT,
  product_name     TEXT,
  sales            NUMERIC(12,2) NOT NULL,
  quantity         INT NOT NULL,
  discount         NUMERIC(5,2) NOT NULL,
  profit           NUMERIC(12,3) NOT NULL,
  shipping_cost    NUMERIC(12,2) NOT NULL,
  order_priority   TEXT,
  year             INT NOT NULL,
  shipping_days    INT NOT NULL
);

-- Optional indexes for BI speed
CREATE INDEX IF NOT EXISTS idx_retail_sales_order_date ON public.retail_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_retail_sales_market ON public.retail_sales(market);
CREATE INDEX IF NOT EXISTS idx_retail_sales_category ON public.retail_sales(category);