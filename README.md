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

## 📊 KPI & Dashboard (In Progress)

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
