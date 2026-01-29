# Executive Retail BI & Forecasting System (PostgreSQL • Power BI • Time Series)

An **executive-ready Business Intelligence + Forecasting** project that transforms raw transactional retail data into:

- **BI-ready KPIs** (Power BI dashboard)
- **revenue forecasts** (next 6 months)
- **actionable business recommendations** (pricing, discounting, profitability)

---

## 🚀 Why This Project

Retail leadership often lacks:

- a single source of truth for KPIs,
- visibility into profitability drivers,
- reliable near-term revenue forecasts for planning.

This project operationalizes an end-to-end workflow:
**CSV → Python ETL → PostgreSQL → SQL KPIs → Power BI → Forecasting Model → Executive Summary**

---

## 🎯 Business Objective

Build a **production-style analytics system** that enables executives to:

1. monitor sales & profit performance,
2. identify drivers of growth and losses,
3. forecast monthly revenue for the next 6 months,
4. act on insights (discount strategy, category focus, regional performance).

---

## 🧾 Dataset

**File:** `superstore_sales_clean.csv`  
**Granularity:** one row per **order line item**  
**Core entities:** Orders • Customers • Products • Geography • Time

Key fields include:

- `sales`, `profit`, `quantity`, `discount`, `shipping_cost`
- `order_date`, `ship_date`, `market`, `region`, `category`, `sub_category`

---

## 🏗️ Architecture

```text
Raw CSV
  ↓
Python ETL (type casting • date parsing • validation • derived features)
  ↓
PostgreSQL (staging → production)
  ↓
SQL KPI Views (BI-ready aggregations)
  ↓
Power BI Dashboard (Executive reporting)
  ↓
Time Series Forecasting (Monthly revenue + evaluation)
  ↓
Business Recommendations
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

---

## 🔍 Key EDA Findings (Executive Summary)

- 51,290 line-item transactions across 25,035 unique orders
- Total Sales: ~$12.6M
- Total Profit: ~$1.47M
- Profit Margin: ~11.6%
- Loss-making rate: ~24.5% of transactions are unprofitable
- Category performance: Technology leads in both revenue and profit
- Furniture: high revenue but lower profit efficiency (margin opportunity)
- Market performance: APAC is the highest revenue-generating market
- Shipping: average delivery time is ~4 days; high shipping costs may erode margins

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

```Create .env in the project root (use .env.example as template):

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
