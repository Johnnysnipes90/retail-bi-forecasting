# 📊 Executive Retail BI & Forecasting System

### PostgreSQL • Power BI • Python ETL • Time-Series Forecasting

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![SQL](https://img.shields.io/badge/SQL-BI%20Views-lightgrey)
![Power BI](https://img.shields.io/badge/Power%20BI-Executive%20Dashboard-yellow)
![Status](https://img.shields.io/badge/Status-In%20Progress-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

An **executive-ready Business Intelligence and Forecasting system** that transforms raw retail transactions into:

- **BI-ready KPIs** for executive dashboards (Power BI)
- **Validated PostgreSQL analytics tables** (single source of truth)
- **Monthly revenue forecasts** (next 6 months) with confidence bounds
- **Actionable insights** on profitability, discounting, and operational performance

This project follows **production-style analytics engineering** practices (SQL-first metrics, validated ETL, reproducible forecasting), not notebook-only analysis.

---

## Business Problem

Retail teams often struggle with:

- fragmented KPI definitions,
- limited visibility into _why_ profit is leaking,
- reactive decision-making without reliable forecasts.

This project operationalizes a **decision-focused analytics workflow** to support reporting, diagnostics, and planning.

---

## Objectives

1. Monitor revenue, profit, margin, orders, and loss rate
2. Identify category, market, and regional performance drivers
3. Detect unprofitable sales patterns (discounting, shipping cost)
4. Forecast monthly revenue for the next **6 months**
5. Translate analytics into executive-ready recommendations

---

## Dataset

- **File:** `superstore_sales_clean.csv`
- **Granularity:** one row per **order line item**
- **Records:** 51,290 rows | 25,035 unique orders

**Key fields**

- Metrics: `sales`, `profit`, `discount`, `quantity`, `shipping_cost`
- Dimensions: `market`, `region`, `category`, `sub_category`, `segment`, `ship_mode`
- Time: `order_date`, `ship_date` (+ engineered `shipping_days`)

---

## System Architecture

```text
Raw CSV
  ↓
Python ETL
  - type casting + date parsing
  - validation rules
  - feature engineering (shipping_days)
  ↓
PostgreSQL
  - strongly typed analytics table
  ↓
SQL Views (BI-ready KPI layer)
  ↓
Power BI Dashboard (executive reporting)
  ↓
Time-Series Forecasting (SARIMA)
  ↓
Forecast table persisted to PostgreSQL for BI
```

---

## ✅ What’s Implemented

### 1) Exploratory Data Analysis (EDA)

- Validated dataset structure, schema, and granularity
- Confirmed date integrity and shipping logic
- Verified no missing values or duplicate records
- Quantified core KPIs: sales, profit, margin, and loss rate
- Identified key category and geographic performance drivers
- Surfaced early risk signals related to discounting and shipping cost

---

### 2) ETL Pipeline → PostgreSQL

- Environment-based configuration using `.env`
- Robust CSV extraction and transformation pipeline
- Strong data validation rules (types, ranges, date logic)
- Idempotent **staging → production** load pattern
- Strongly typed analytics table for BI and forecasting
- Sanity checks confirm PostgreSQL metrics match EDA outputs

---

### 3) SQL KPI Views (Power BI–Ready)

All business logic is implemented **upstream in SQL** to ensure
a single source of truth and minimal BI-layer complexity.

Implemented views:

- `public.vw_exec_kpis`
- `public.vw_monthly_sales`
- `public.vw_category_kpis`
- `public.vw_market_kpis`
- `public.vw_region_profitability`
- `public.vw_shipping_kpis`

These views power both **Power BI dashboards** and **forecasting models**.

---

## 🔍 Executive Summary (Key Findings)

- **51,290** line-item transactions across **25,035** unique orders
- **Total Sales:** ~$12.6M
- **Total Profit:** ~$1.47M
- **Profit Margin:** ~11.6%
- **Loss Rate:** ~24.5% of transactions are loss-making

### Profitability Insights

- Technology leads in both revenue and profit
- Furniture shows elevated loss rates (margin optimization opportunity)
- APAC is the highest revenue-generating market
- EMEA exhibits margin compression

### Operational Signals

- Average shipping time ≈ 4 days
- High shipping costs combined with aggressive discounting
  materially contribute to profit leakage

---

## 📊 Power BI Executive Dashboard

A multi-page executive Power BI dashboard built directly on
PostgreSQL KPI views, ensuring:

- **Single source of truth** for all metrics
- **Minimal DAX complexity** (SQL handles business logic)
- Clean semantic model with fast refresh performance

### Dashboard Pages

#### 1) Executive Overview

**Answers:** _“How is the business performing?”_

- KPI cards:
  - Total Sales
  - Total Profit
  - Profit Margin %
  - Total Orders
  - Loss Rate %
- Monthly revenue trend
- Sales by market
- Top sub-categories by revenue and margin

---

#### 2) Profitability & Risk

**Answers:** _“Where are we leaking money?”_

- Discount vs Profitability scatter
  (sub-category level, sized by revenue)
- Loss rate by market (risk flags)
- Profit margin by region
- Executive narrative summary highlighting:
  - ~24.5% loss-making transactions
  - Margin compression in EMEA
  - Elevated loss rates in Furniture

---

#### 3) Operations (Shipping Performance)

**Answers:** _“Are shipping decisions hurting margin?”_

- Average shipping days by ship mode
- Average shipping cost by ship mode
- Shipping KPI table:
  - Sales
  - Profit
  - Profit Margin (conditional risk formatting)

---

### Dashboard Assets

- Power BI file: `dashboards/Executive_Retail_BI_Forecasting.pbix`
- Screenshots: `dashboards/screenshots/`

---

## 📈 Revenue Forecasting (Monthly)

Monthly revenue is forecasted using a **Seasonal ARIMA (SARIMA)** model
trained on validated PostgreSQL analytics data (single source of truth).

### Data

- Source: `public.vw_monthly_sales`
- Frequency: Monthly (Month Start)
- History: 48 months (2011–2014)

### Modeling Approach

- Seasonal decomposition confirms trend and annual seasonality
- ADF test indicates non-stationarity → differencing applied
- Model: **SARIMA(1,1,1)(0,1,1,12)**
  - `d = 1` captures trend
  - `D = 1, s = 12` captures annual seasonality
- Evaluation via leakage-free holdout backtest (last 6 months)
- Metrics: MAE, RMSE, **sMAPE** (robust percentage error)

### Backtest Performance (Holdout: last 6 months)

|                     Model |        MAE |       RMSE |      sMAPE |
| ------------------------: | ---------: | ---------: | ---------: |
| Seasonal Naive (baseline) |    111,973 |    121,002 |     27.67% |
|                **SARIMA** | **70,220** | **79,585** | **16.09%** |

The SARIMA model significantly outperforms the baseline,
providing **planning-grade accuracy** for executive forecasting.

### Forecast Output

- 6-month revenue forecast
- 95% confidence intervals (lower / upper bounds)
- Forecast vs Actual backtest visualization
- Forecast table persisted to PostgreSQL for BI:

`public.monthly_sales_forecast`  
Columns:

- `month`
- `actual_sales`
- `forecast_sales`
- `ci_lower`
- `ci_upper`
- `run_type`

---

## 🧰 Tech Stack

- **Python:** pandas, numpy, SQLAlchemy, psycopg2, python-dotenv,
  statsmodels, scikit-learn
- **Database:** PostgreSQL
- **Analytics Layer:** SQL (views + KPI aggregation)
- **BI:** Power BI
- **Forecasting:** SARIMA (statsmodels)

---

## ▶️ How to Run Locally

### 1) Create `.env`

Create `.env` in the project root (use `.env.example` as template):

```env
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=retail_bi
PG_USER=postgres
PG_PASSWORD=your_password
PG_SCHEMA=public
RAW_CSV_PATH=data/raw/superstore_sales_clean.csv
```

### 2) Create Tables

```psql -h localhost -p 5432 -U postgres -d retail_bi -f sql/00_schema.sql

```

### 3) Run ETL (CSV → PostgreSQL)

```python src/etl_load_postgres.py

```

### 4) Create BI Views

```psql -h localhost -p 5432 -U postgres -d retail_bi -f sql/10_bi_views.sql

```

### 5) Sanity Checks

```psql -h localhost -p 5432 -U postgres -d retail_bi -f sql/99_sanity_checks.sql
psql -h localhost -p 5432 -U postgres -d retail_bi -f sql/11_view_sanity.sql
```

### 6) Run Forecasting Pipeline (Module)

This runs the SARIMA pipeline and writes output to:

- data/processed/backtest_forecast.csv
- data/processed/monthly_forecast.csv
- PostgreSQL table: public.monthly_sales_forecast

```python src/run_forecast.py

```

---

## 📁 Repository Structure

```
retail-bi-forecasting/
├── dashboards/
│   ├── Executive_Retail_BI_Forecasting.pbix
│   └── screenshots/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_monthly_revenue_forecasting.ipynb
├── sql/
│   ├── 00_schema.sql
│   ├── 10_bi_views.sql
│   ├── 11_view_sanity.sql
│   ├── 20_forecast_table.sql
│   └── 99_sanity_checks.sql
├── src/
│   ├── forecasting/
│   │   ├── __init__.py
│   │   └── sarima_forecast.py
│   ├── etl_load_postgres.py
│   ├── validation.py
│   └── run_forecast.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🧠 Business Value

- Enables proactive planning through reliable revenue forecasts
- Flags unprofitable patterns driven by discounting and shipping costs
- Improves executive visibility via standardized KPI dashboards
- Transitions analytics from reactive → diagnostic → predictive

# 📊 Executive Retail BI & Forecasting System

### PostgreSQL • Power BI • Python ETL • Time Series Forecasting

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![SQL](https://img.shields.io/badge/SQL-BI%20Views-lightgrey)
![Power BI](https://img.shields.io/badge/Power%20BI-Executive%20Dashboard-yellow)
![Status](https://img.shields.io/badge/Project%20Status-In%20Progress-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Project Overview

An **executive-ready Business Intelligence and Forecasting system** that transforms raw retail transaction data into:

- **BI-ready KPIs** for executive dashboards (Power BI)
- **Clean, validated PostgreSQL analytics tables**
- **Monthly revenue forecasts** (next 6 months)
- **Actionable business recommendations** on profitability, discounting, and regional performance

This project is built using **production-style data engineering and analytics practices**, not notebook-only analysis.

---

## 🚀 Why This Project Exists

Retail leadership teams often struggle with:

- fragmented KPI definitions,
- limited visibility into _why_ profit is leaking,
- reactive decision-making without reliable forecasts.

This project operationalizes a **single source of truth** and a **decision-focused analytics workflow** that supports planning, optimization, and executive reporting.

---

## 🎯 Business Objectives

Build an end-to-end analytics system that enables executives to:

1. Monitor revenue, profit, margin, and loss rates
2. Identify category, market, and regional performance drivers
3. Detect unprofitable sales patterns (discounting, shipping costs)
4. Forecast monthly revenue for the next **6 months**
5. Translate analytics into **clear business actions**

---

## 🧾 Dataset

- **File:** `superstore_sales_clean.csv`
- **Granularity:** One row per **order line item**
- **Records:** 51,290 rows | 25,035 unique orders

### Core Entities

- Orders
- Customers
- Products
- Geography (Market, Region, Country)
- Time

### Key Metrics

- `sales`, `profit`, `quantity`, `discount`, `shipping_cost`
- `order_date`, `ship_date`, `market`, `region`, `category`, `sub_category`

---

## 🏗️ System Architecture

```text
Raw CSV
  ↓
Python ETL
  - type casting
  - date parsing
  - validation rules
  - feature engineering
  ↓
PostgreSQL
  - staging table
  - production analytics table
  ↓
SQL Views
  - BI-ready KPI aggregations
  ↓
Power BI Dashboard
  - executive reporting
  ↓
Time Series Forecasting
  - monthly revenue predictions
  ↓
Executive Insights & Recommendations

```

---

## ✅ What’s Implemented (So Far)

**EDA**

- Confirmed dataset shape and granularity
- Validated dates and shipping logic
- Quantified overall sales, profit, margin, and loss rate
- Identified category and geographic performance signals

**ETL to PostgreSQL**

- Robust environment config via .env
- CSV extraction + transformations + BI-safe validation rules
- Staging → Production load pattern (idempotent reruns)
- Strongly typed production table for BI + forecasting
- Sanity-checked metrics against EDA

---

## 🔍 Key EDA Findings (Executive Summary)

- 51,290 line-item transactions across 25,035 unique orders
- Total Sales: ~$12.6M
- Total Orders: 25,035
- Total Profit: ~$1.47M
- Profit Margin: ~11.6%
  **Profitability Insights**
- Loss-making rate: ~24.5% of transactions are unprofitable
- Category performance: Technology leads in both revenue and profit
- Furniture: high revenue but lower profit efficiency (margin opportunity)
- Market performance: APAC is the highest revenue-generating market
  **Operational Signals**
- Average shipping time ≈ 4 days
- High shipping costs and aggressive discounting contribute to losses

---

## 📊 KPI & Dashboard

Planned Power BI pages:

- Executive Overview: Revenue, Profit, Margin, MoM trend
- Sales Trends: monthly trend + seasonality
- Category & Product: top/bottom categories, sub-category drilldowns
- Geography: market and region performance + profitability flags

Screenshots and .pbix is live in: dashboards/

---

## 📈 Forecasting

We will forecast monthly revenue for the next 6 months using a time-series model (SARIMA or Prophet).

Model evaluation will include:

- MAE
- RMSE
- MAPE

**Expected output:**

- forecast plot (history vs prediction)
- forecast table with confidence intervals
- recommendation summary for planning

---

## 🧰 Tech Stack

Python: pandas, numpy, SQLAlchemy, psycopg2, python-dotenv

- Database: PostgreSQL
- Analytics: SQL (views + KPI aggregation)
- BI: Power BI
- Forecasting: statsmodels / Prophet (TBD)

---

## ▶️ How to Run Locally

- 1. Create environment

```Create .env in the project root (i used .env.example as template):

PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=retail_bi
PG_USER=postgres
PG_PASSWORD=your_password
PG_SCHEMA=public
RAW_CSV_PATH=data/raw/superstore_sales_clean.csv
```

- 2. Create tables (schema)

**Run:**

```
sql/00_schema.sql
```

- 3. Run ETL (CSV → PostgreSQL)

```
python src/etl_load_postgres.py
```

- 4. Verify load

```SELECT COUNT(*) FROM public.retail_sales;

```

---

## 📁 Repository Structure

```retail-bi-forecasting/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 01_eda.ipynb
├── src/
│   ├── etl_load_postgres.py
│   └── validation.py
├── sql/
│   └── 00_schema.sql
├── dashboards/
│   └── screenshots/
└── README.md
```

---

🧠 Business Impact (Planned Outcomes)

- Enables proactive inventory and staffing decisions via forecasts
- Flags unprofitable segments (discount + shipping-driven losses)
- Improves executive visibility and strategy alignment through KPI dashboards.

---

## 📈 Revenue Forecasting (Monthly)

Monthly revenue is forecasted using a **Seasonal ARIMA (SARIMA)** model trained on
validated PostgreSQL analytics data (single source of truth via SQL views).

---

### Data

- Source: `public.vw_monthly_sales`
- Frequency: Monthly (Month Start)
- History: 48 months (2011–2014)

### Modeling Approach

- Seasonal decomposition used to confirm trend + annual seasonality
- ADF test indicates non-stationarity → differencing required
- Model: **SARIMA(1,1,1)(0,1,1,12)**
  - `d=1` captures trend (non-stationarity)
  - `D=1, s=12` captures annual seasonality
- Evaluation: leakage-free holdout backtest (last 6 months)
- Metrics: MAE, RMSE, **sMAPE** (robust percentage error)

### Backtest Performance (Holdout: last 6 months)

|                     Model |        MAE |       RMSE |      sMAPE |
| ------------------------: | ---------: | ---------: | ---------: |
| Seasonal Naive (baseline) |    111,973 |    121,002 |     27.67% |
|                    SARIMA | **70,220** | **79,585** | **16.09%** |

SARIMA significantly outperforms the baseline, providing **planning-grade accuracy**
for executive scenario analysis.

### Forecast Output

- 6-month revenue forecast
- 95% confidence intervals (lower / upper bounds)
- Backtest plot (Forecast vs Actual)
- Forecast table persisted to PostgreSQL for BI:

`public.monthly_sales_forecast`  
Columns: `month`, `actual_sales`, `forecast_sales`, `ci_lower`, `ci_upper`, `run_type`
