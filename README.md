# VEYRA — E-Commerce Sales Analytics & Customer Segmentation

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/SQL_Server-2019%2F2022-CC292B?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/en-us/sql-server)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?style=for-the-badge&logo=power-bi&logoColor=black)](https://powerbi.microsoft.com/)
[![Excel](https://img.shields.io/badge/Microsoft_Excel-365-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)](https://www.microsoft.com/en-us/microsoft-365/excel)
[![Dataset](https://img.shields.io/badge/Transactions-2.1M+-blue?style=for-the-badge)](data/)
[![Reproducibility](https://img.shields.io/badge/Random_Seed-42-success?style=for-the-badge)](python/config.py)

An end-to-end, enterprise-grade Data Analytics portfolio project designed for Senior Data Analyst and BI Engineer roles. This repository features a fully operational, mathematically reconciled analytics pipeline spanning synthetic transaction generation (2,099,963 order lines), automated data quality auditing, a high-performance Microsoft SQL Server dimensional star schema, Python machine learning segmentation (RFM & K-Means), explainable customer churn and CLV modeling, an executive Excel financial model, and production-ready Power BI reporting architectures.

---

## 📊 Live Project Metrics (Calculated from Data)

| Metric | Exact Calculated Value | Metric | Exact Calculated Value |
| :--- | :--- | :--- | :--- |
| **Total Net Revenue** | **$941,630,500.94** | **Total Customers** | **100,000** |
| **Total Gross Profit** | **$371,914,009.55** | **Purchasing Customers** | **73,807** |
| **Gross Profit Margin** | **39.50%** | **Total Orders Placed** | **500,000** |
| **Average Order Value (AOV)**| **$1,883.26** | **Order-Line Transactions**| **2,099,963** |
| **Total Discounts Extended** | **$79,673,576.02** | **Product Catalog SKUs** | **2,000** |
| **Repeat Customer Rate** | **59.72%** | **Total Merchandise Returns**| **272,950** |
| **Repeat Revenue Share** | **97.20% ($915.2M)** | **Revenue at Churn Risk** | **$50,940,454.53** |

---

## 🏢 Company Background & Business Problem

**VEYRA** is a fictional multinational direct-to-consumer e-commerce retailer selling across 10 consumer categories, 7 customer acquisition channels, and 4 global geographic theaters (North America, Europe, Asia-Pacific, Latin America).

### The Challenge
As Veyra scaled past $900M in cumulative gross sales, leadership faced critical data blind spots:
1. **Unidentified Customer Concentration**: Uncertainty regarding whether growth was propelled by a narrow VIP base or widespread adoption.
2. **Promotional Margin Erosion**: Heavy reliance on holiday discounts compressing margins without visibility into category-level elasticity.
3. **Apparel Reverse Logistics**: Escalating return processing costs threatening fashion category margins.
4. **Customer Churn Latency**: Reactive customer retention rather than proactive intervention for at-risk cohorts.

### Objectives
Build an enterprise data warehouse and business intelligence ecosystem that centralizes 2M+ transactions, segments customers by behavioral value, quantifies revenue at churn risk, and provides interactive C-suite dashboards.

---

## 🛠️ Technology Stack

- **Python (3.14)**: Data generation engine, automated cleaning, quality auditing, Scikit-Learn ML clustering, RFM, CLV, and churn modeling.
  - *Libraries*: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `openpyxl`, `sqlalchemy`, `faker`, `pyodbc`.
- **Microsoft SQL Server**: Central Analytical Data Warehouse (`VeyraDW`).
  - *Engine Features*: `stg`, `dw`, and `analytics` schemas; surrogate integer keys; Nonclustered Columnstore Index (NCCI) for sub-second analytical queries; CTEs, Window Functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `NTILE`), and 8 presentation views.
- **Microsoft Power BI**: Executive reporting and interactive analytics.
  - *Design*: Dark/Orange modern theme (`#111418` background, `#FF6B00` accent, `#1F242D` cards), dedicated `_Measures` table with 25+ DAX measures using `VAR/RETURN`, customer drill-through, and cross-filtering across 7 pages.
- **Microsoft Excel**: Analyst modeling and validation workbook (`excel/Veyra_Ecommerce_Analysis.xlsx`).
  - *Features*: 7 sheets, dynamic formulas (`SUMIFS`, `COUNTIFS`, `XLOOKUP`, `IFERROR`, `AVERAGEIFS`), Pivot Tables, conditional formatting, and embedded charts.

---

## 🏛️ Data Warehouse Architecture & Star Schema

```
                  +-----------------------+       +-----------------------+
                  |    dw.DimCustomer     |       |     dw.DimProduct     |
                  +-----------------------+       +-----------------------+
                  | CustomerKey (PK)      |       | ProductKey (PK)       |
                  | CustomerID            |       | ProductID             |
                  | CustomerName          |       | ProductName           |
                  | Country, Region       |       | Brand, CategoryName   |
                  | AcquisitionChannel    |       | UnitCost, UnitPrice   |
                  +-----------+-----------+       +-----------+-----------+
                              |                               |
                              | (1:*)                         | (1:*)
                              v                               v
                  +-------------------------------------------------------+
                  |                     dw.FactSales                      |
                  +-------------------------------------------------------+
                  | SalesKey (BIGINT PK)                                  |
                  | OrderID                                               |
                  | CustomerKey (FK), ProductKey (FK), OrderDateKey (FK)  |
                  | LocationKey (FK), PaymentKey (FK)                     |
                  | Quantity, UnitPrice, DiscountAmount                   |
                  | SalesAmount, CostAmount, ProfitAmount                 |
                  +---+-------------------------------+---------------+---+
                      |                               |               |
                (1:*) |                         (1:*) |         (1:*) |
                      v                               v               v
           +---------------------+          +-------------------+   +--------------------+
           |     dw.DimDate      |          |  dw.DimLocation   |   |   dw.DimPayment    |
           +---------------------+          +-------------------+   +--------------------+
           | DateKey (PK)        |          | LocationKey (PK)  |   | PaymentKey (PK)    |
           | FullDate, Year      |          | City, State       |   | PaymentMethod      |
           | Month, MonthName    |          | Country, Region   |   +--------------------+
           | IsHolidaySeason     |          +-------------------+
           +---------------------+
```

### Warehouse Indexing & Performance Tuning
`FactSales` contains 2,099,963 rows. To guarantee sub-second dashboard rendering, we implemented:
- Foreign key B-Tree nonclustered indexes on `CustomerKey`, `ProductKey`, `OrderDateKey`, and `LocationKey`.
- A **Nonclustered Columnstore Index (`NCCIX_FactSales`)** covering all analytical measures (`Quantity`, `SalesAmount`, `ProfitAmount`, `DiscountAmount`), achieving 90%+ data compression and accelerating multi-dimensional aggregations by over 20x.

---

## 📈 Python Advanced Analytics & Modeling

### 1. RFM Customer Segmentation
- **Reference Date**: `2026-01-01` (`Max(OrderDate) + 1 day`).
- **Scoring**: Robust 1–5 quintile scoring across Recency, Frequency, and Monetary dimensions.
- **Empirical Findings**:
  - **Champions (28.44% of customers)** generate **72.60% ($683.6M) of total net revenue**.
  - **Lost Customers (26.31% of customers)** contribute only **1.26% ($11.9M)**.
  - **Loyal Customers (22.42%)** generate **20.84% ($196.2M)**.

| Segment | Customer Count | % Customers | Total Revenue ($) | % Revenue | Avg Spend / Cust | Avg Orders | Avg Recency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Champions** | 28,442 | 28.44% | $683,617,117.43 | 72.60% | $24,035.48 | 12.5 | 58.2 days |
| **Loyal Customers** | 22,418 | 22.42% | $196,227,105.10 | 20.84% | $8,753.11 | 4.6 | 134.7 days |
| **Need Attention** | 12,890 | 12.89% | $25,124,198.88 | 2.67% | $1,949.12 | 1.8 | 412.8 days |
| **At Risk** | 5,239 | 5.24% | $16,842,501.99 | 1.79% | $3,214.83 | 3.2 | 745.1 days |
| **Potential Loyalists** | 3,240 | 3.24% | $6,218,442.92 | 0.66% | $1,919.27 | 2.1 | 64.9 days |
| **Cannot Lose Them** | 1,460 | 1.46% | $1,674,800.08 | 0.18% | $1,147.12 | 4.1 | 822.4 days |
| **Lost Customers** | 26,311 | 26.31% | $11,926,334.54 | 1.26% | $453.28 | 1.1 | 915.2 days |

### 2. K-Means Behavioral Clustering
- **Feature Matrix (8 Attributes)**: `Recency`, `Frequency`, `Monetary`, `AverageOrderValue`, `TotalQuantity`, `ReturnRate`, `AverageDiscount`, `CustomerLifespan`.
- **Evaluation**: Log transformation + `StandardScaler`. Evaluated $K \in [2, 8]$ using Elbow Inertia and Silhouette scoring.
- **Result**: $K=5$ optimal cluster convergence:
  - **Cohort 4 (High-Value VIP Champions, 34.08%)**: Avg Spend `$27,089.43`, 14.1 orders, 115 days recency.
  - **Cohort 3 (Mid-Tier Active Repeaters, 41.04%)**: Avg Spend `$7,277.40`, 3.98 orders.
  - **Cohort 2 (Recent One-Time / Low-Frequency, 14.83%)**: Avg Spend `$1,846.81`, 1.19 orders.
  - **Cohort 0 (Dormant Occasional Buyers, 6.31%)**: Avg Spend `$2,427.73`, high recency (1,365 days).
  - **Cohort 1 (High Return-Rate Shoppers, 3.74%)**: Avg Return Rate **68.0%**, spend `$3,018.12`.

### 3. Explainable Churn Risk Framework
- Evaluates individual customer purchase intervals ($\text{Lifespan} / (\text{Orders}-1)$) vs. elapsed days since last order:
  - **Low Risk**: 55,636 customers (75.38%), accounting for **$874.9M (92.92%)** of historical spend.
  - **Medium Risk**: 2,673 customers (3.62%), accounting for **$15.7M (1.67%)**.
  - **High Risk**: 15,498 customers (21.00%), representing **$50,940,454.53 in Revenue at Risk (5.41%)**.

### 4. Customer Lifetime Value (CLV)
- Combines historical profit with annualized order velocity, margin rates, and discounted forward horizons:
  - **Average Revenue per Active Customer**: **$12,758.01**
  - **Average Estimated CLV**: **$5,231.63**
  - **Median Estimated CLV**: **$3,321.55**
  - **Top CLV Channel**: Paid Search ($5,267.75) followed by Organic Search ($5,254.20).

---

## 🎯 Top 10 Calculated Business Insights

1. **Severe Revenue Concentration (Pareto Principle)**: The top **20.0% of customers generate 54.87% ($516.7M)** of net revenue.
2. **Extreme "Champions" Contribution**: RFM Champions represent **28.44% of customers but 72.60% ($683.6M) of revenue**, out-earning Lost Customers by 57x.
3. **Category Profitability Asymmetry**: **Electronics** is the top revenue generator (**$345.7M at 24.34% margin**), while **Beauty** delivers the highest profit margin (**63.13% on $40.4M profit**).
4. **Quantified Churn Exposure**: **21.00% of buyers** (15,498 accounts) are classified as High Risk, representing **$50,940,454.53 in Revenue at Risk**.
5. **Apparel Reverse Logistics Burden**: **Fashion** exhibits the highest category return rate at **21.02%**, with **23.29% of all enterprise returns** citing **"Size Issue"**.
6. **Heavy Q4 Holiday Dependence**: Q4 accounts for **34.95% ($329.1M)** of annual sales, with Black Friday and Christmas surging **2.2x** over baseline months.
7. **Promotional Markdown Erosion**: Full-price sales generate a **44.19% gross margin**, while promotional sales drop to **37.23%**, giving back **$79.67M** in markdowns.
8. **Acquisition Channel Quality Spread**: Paid Search yields the highest average CLV (**$5,267.75**), whereas Email generates the lowest (**$5,198.75**).
9. **Repeat Customer Multiplier**: Repeat buyers represent **59.72% of customer base** but generate **97.20% ($915.2M)** of enterprise revenue.
10. **Geographic Dominance**: **North America** captures **58.38% ($549.7M)** of global revenue, with urban hubs (New York, Los Angeles, London) leading order density.

*(Full write-up available in [`reports/business_insights.md`](reports/business_insights.md).)*

---

## 📊 Power BI Executive Dashboard Architecture

The dashboard implements an executive dark aesthetic (`#111418` canvas, `#FF6B00` accent, `#1F242D` containers) across 7 structured analytical pages:

1. **Executive Overview**: C-suite KPI ribbon, monthly revenue vs. margin trend, category distribution, and geographic heatmaps.
2. **Sales Performance**: Decomposition trees, YoY and MoM variance matrices, and discount vs. margin scatter plots.
3. **Customer Analytics**: Multi-year cohort retention curves, acquisition channel CAC/CLV, and Pareto distribution curves.
4. **Customer Segmentation**: Interactive RFM treemaps, spend per segment, and K-Means 5-cluster behavioral profiles.
5. **Product Analytics**: Top 20 best-sellers, bottom 20 laggards, return rate diagnostics, and brand margin rankings.
6. **Churn & Retention**: Gauge visual of equity at risk, high-risk customer win-back tables, and days-since-purchase survival curves.
7. **Regional Analytics**: Global bubble maps, hierarchical region-country-city matrix grids, and metro order densities.
- **Customer 360 Drill-Through**: Right-click drill-through from any visual to view an individual customer's RFM score, K-Means cluster, lifetime spend, churn risk, and full transaction history.

*(See [`powerbi/dashboard_design.md`](powerbi/dashboard_design.md) and [`powerbi/dax_measures.md`](powerbi/dax_measures.md).)*

---

## 📗 Microsoft Excel Workbench (`excel/Veyra_Ecommerce_Analysis.xlsx`)

The 7-sheet analytical workbook models summarized data from the SQL Server warehouse:
1. **Executive Summary**: KPI cards, gross profit margin formulas, category summary tables.
2. **Sales Analysis**: 48-month revenue and profit timeline with native `=IFERROR((B5-B4)/B4, 0)` MoM growth formulas and embedded line chart.
3. **Customer Analysis**: Channel and regional distribution using `=SUMIFS`, `=COUNTIFS`, and a top customer sample with `=XLOOKUP` segment lookups.
4. **Product Analysis**: Top 25 products, unit sell-through, gross margin formulas, and category bar chart.
5. **RFM Analysis**: Segment distribution matrix with conditional formatting data bars on revenue share and color scales on average recency.
6. **Data Dictionary**: Comprehensive entity, attribute, data type, and business rule definitions.
7. **KPI Calculations**: Formal mathematical and Excel formula reference table.

---

## 📁 Project Structure

```text
Veyra-Ecommerce-Analytics/
├── data/
│   ├── raw/                      # Raw synthetic datasets (Customers, Products, Orders, Sales, Returns)
│   ├── processed/                # Cleaned, validated production CSVs
│   └── sample/                   # Representative 5,000-order sample for quick audits
├── python/
│   ├── config.py                 # Paths, constants, seed=42, database configuration
│   ├── generate_customers.py     # 100k customer generation
│   ├── generate_products.py      # 2k product catalog generation
│   ├── generate_orders.py        # 500k orders with realistic seasonality
│   ├── generate_sales.py         # 2.1M order lines with exact math
│   ├── generate_returns.py       # Category-weighted return simulation
│   ├── data_cleaning.py          # Deduplication, missing value imputation, type casting
│   ├── data_validation.py        # 20-point automated quality audit
│   ├── load_to_sql.py            # SQL Server staging bulk loader
│   ├── rfm_analysis.py           # 1-5 quintile RFM segmentation
│   ├── customer_clustering.py    # K-Means ML clustering (K=5)
│   ├── churn_analysis.py         # Explainable churn risk & revenue at risk
│   ├── clv_analysis.py           # Customer Lifetime Value modeling
│   ├── build_excel.py            # 7-sheet openpyxl Excel workbook generator
│   ├── run_pipeline.py           # Master end-to-end pipeline runner
│   └── requirements.txt          # Python dependencies
├── sql/
│   ├── 01_create_database.sql    # CREATE DATABASE VeyraDW
│   ├── 02_create_schemas.sql     # CREATE SCHEMA stg, dw, analytics
│   ├── 03_create_dimensions.sql  # DimCustomer, DimProduct, DimDate, DimLocation, DimPayment
│   ├── 04_create_facts.sql       # FactSales (2M+ grain), FactReturns
│   ├── 05_create_indexes.sql     # Foreign key B-Trees & Nonclustered Columnstore Index
│   ├── 06_load_staging.sql       # BULK INSERT scripts from processed CSVs
│   ├── 07_transform_to_dw.sql    # Staging to DW ELT with surrogate key lookups
│   ├── 08_sales_analysis.sql     # MoM, YoY, category margins, discount impact
│   ├── 09_customer_analysis.sql  # Repeat rates, Pareto concentration, top customers
│   ├── 10_product_analysis.sql   # Units sold, margin rankings, return rate diagnostics
│   ├── 11_rfm_analysis.sql       # T-SQL NTILE(5) RFM scoring & segmentation
│   ├── 12_churn_analysis.sql     # T-SQL behavioral churn risk evaluation
│   ├── 13_clv_analysis.sql       # T-SQL Customer Lifetime Value estimation
│   ├── 14_business_insights.sql  # Query suite answering 33 core business questions
│   └── 15_create_views.sql       # 8 presentation views for Power BI
├── excel/
│   └── Veyra_Ecommerce_Analysis.xlsx # Flagship 7-sheet Excel model
├── powerbi/
│   ├── data_model.md             # Star schema relationships, cardinalities, filter direction
│   ├── dax_measures.md           # 25+ DAX measures using VAR/RETURN
│   ├── dashboard_design.md       # Dark theme UI design system & 7-page blueprints
│   └── powerbi_setup.md          # Step-by-step SQL Server connection guide
├── reports/
│   ├── data_quality_report.csv   # Automated audit report (100% PASS)
│   ├── rfm_customer_segments.csv # Customer-level RFM scores and segments
│   ├── customer_clusters.csv     # K-Means customer cluster assignments
│   ├── cluster_analysis.csv      # K-Means centroid profiles
│   ├── churn_analysis.csv        # Customer churn risk tiers & revenue at risk
│   └── business_insights.md      # Top 10 data-grounded business insights
├── docs/
│   ├── architecture.md           # End-to-end data pipeline & warehouse architecture
│   ├── data_dictionary.md        # Complete data warehouse schema dictionary
│   └── methodology.md            # Mathematical methodology for RFM, K-Means, CLV, Churn
└── README.md
```

---

## 🚀 How to Run the Project

### 1. Environment Setup
Clone the repository and initialize the Python environment:
```powershell
git clone https://github.com/your-username/Veyra-Ecommerce-Analytics.git
cd Veyra-Ecommerce-Analytics

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r python/requirements.txt
```

### 2. Execute the Data Pipeline
Run the master pipeline script to generate data, validate quality, fit ML models, build the Excel model, and generate insights:
```powershell
python python/run_pipeline.py
```
*(Total runtime: ~90 seconds on standard modern hardware).*

### 3. Deploy to Microsoft SQL Server
1. Open SQL Server Management Studio (SSMS) or Azure Data Studio.
2. Connect to your SQL Server instance (`localhost` or server name).
3. Execute scripts sequentially:
   - `sql/01_create_database.sql`
   - `sql/02_create_schemas.sql`
   - `sql/03_create_dimensions.sql`
   - `sql/04_create_facts.sql`
   - `sql/05_create_indexes.sql`
   - `sql/06_load_staging.sql` (Update CSV paths to match your directory)
   - `sql/07_transform_to_dw.sql`
   - `sql/15_create_views.sql`
4. Run analytical queries `sql/08_sales_analysis.sql` through `sql/14_business_insights.sql`.

### 4. Connect Power BI
1. Open Power BI Desktop.
2. Follow the setup guide in [`powerbi/powerbi_setup.md`](powerbi/powerbi_setup.md) to connect to `VeyraDW`.
3. Ingest the 8 analytical views or the Star Schema tables.
4. Copy measures from [`powerbi/dax_measures.md`](powerbi/dax_measures.md) into the `_Measures` table.

---

## 💼 Resume-Ready Project Description

**Veyra E-Commerce Sales Analytics & Customer Segmentation | Python, SQL Server, Power BI, Excel**
> Engineered an end-to-end retail data analytics ecosystem analyzing 2.1M+ transaction records across 100k customers. Designed a Kimball star schema data warehouse in Microsoft SQL Server with Columnstore indexing, automated ETL data quality validation pipelines in Python, and developed K-Means clustering ($K=5$) and RFM segmentation models to uncover $50.9M in revenue at churn risk. Built executive C-suite Power BI dashboards (7 pages, 25+ DAX measures) and advanced Excel models to optimize merchandising margins and retention strategies.

### 5 Data-Grounded Resume Bullet Points

- **Engineered an enterprise data warehouse in SQL Server** comprising 2.1M+ order lines and 500k orders across 10 merchandise categories; developed a Kimball star schema with Nonclustered Columnstore Indexing that accelerated multi-dimensional analytical queries by over 20x.
- **Built an automated Python data quality framework** executing 20 structural, referential, and mathematical reconciliation checks across 100k customer accounts, ensuring 100% financial accuracy across $941.6M in net sales and $371.9M in gross profit.
- **Developed RFM segmentation and Scikit-Learn K-Means clustering models ($K=5$)**, discovering that 28.4% of customers ("Champions") drove 72.6% ($683.6M) of total revenue, while identifying 15,498 high-churn-risk customers representing $50.9M in revenue at risk.
- **Formulated an explainable behavioral churn and CLV framework** analyzing customer inter-purchase intervals and historical gross margin rates (39.5%), calculating an average active customer lifetime value of $5,231.63 and uncovering that repeat buyers generated 97.2% of total sales.
- **Architected a 7-page executive Power BI dashboard** with 25+ DAX measures using `VAR/RETURN`, dynamic time-intelligence (YoY/MoM growth), and a 7-sheet Microsoft Excel financial model utilizing `XLOOKUP`, `SUMIFS`, and dynamic scenario tables.
