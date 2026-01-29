# Executive Retail BI & Forecasting System

## Business Problem

Retail leadership needs visibility into sales performance and reliable revenue forecasts.

## Objective

Build an end-to-end BI and forecasting system to support executive decision-making.

## Data

Transactional retail sales data including date, product, region, quantity, and revenue.

## Approach

- ETL pipeline using Python
- KPI analysis using SQL
- Interactive Power BI dashboard
- Time-series forecasting for revenue prediction

## 🔍 Key EDA Findings

- The dataset contains 51,290 line-item transactions across 25,035 unique orders.
- Overall revenue is $12.6M with a profit margin of 11.6%.
- Approximately 24.5% of transactions are loss-making.
- Technology is the strongest category in both revenue and profit.
- Furniture generates high revenue but comparatively low profit.
- APAC is the highest revenue-generating market.
- Several regions show weak profitability despite strong sales.
- Average shipping time is 4 days, but high shipping costs may erode margins.

## Results

- Identified key revenue drivers
- Detected strong seasonal patterns
- Forecasted next 6 months revenue with X% MAPE

## Business Impact

- Enables proactive inventory planning
- Improves executive visibility
- Supports data-driven strategy

## Tech Stack

Python, SQL, Power BI, Statsmodels

## Next Steps

- Automate pipeline
- Deploy dashboard
- Integrate real-time data
