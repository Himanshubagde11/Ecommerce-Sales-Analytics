# VEYRA E-Commerce Data Architecture & ETL Pipeline

This document details the enterprise data architecture, data layers, transformation workflows, and warehousing structures powering the Veyra Analytics platform.

---

## 1. End-to-End Data Pipeline Flow

```
+-------------------------------------------------------------------------+
|                              INGESTION LAYER                            |
|  Synthetic Data Engine (NumPy, Pandas, Faker)                           |
|  • 100,000+ Customers | 2,000+ Products | 500,000+ Orders               |
|  • 2,000,000+ Transaction Lines | Seasonality & Power-Law Distributions |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                            DATA QUALITY & CLEANING                      |
|  Python Automated Quality Engine                                        |
|  • Deduplication & Referential Integrity Audit                          |
|  • Mathematical Reconciliation: SalesAmount = Qty * Price - Discount    |
|  • Chronological Sequencing: OrderDate >= SignupDate                    |
|  • Produces reports/data_quality_report.csv                             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           SQL SERVER STAGING LAYER                      |
|  VeyraDW.stg Schema                                                     |
|  • stg.Customers | stg.Products | stg.Orders | stg.Sales | stg.Returns  |
|  • Ingested via fast_executemany / BULK INSERT                          |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        DATA WAREHOUSE STAR SCHEMA                       |
|  VeyraDW.dw Schema                                                      |
|  • DimCustomer, DimProduct, DimCategory, DimDate, DimLocation,          |
|    DimPayment (Surrogate Integer Keys)                                  |
|  • FactSales (2M+ Grain) & FactReturns                                  |
|  • Nonclustered Columnstore Index (NCCI) for Sub-Second Aggregations    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                            ANALYTICS VIEWS LAYER                        |
|  VeyraDW.analytics Schema (8 Production Views)                          |
|  • vw_MonthlySales, vw_CategoryPerformance, vw_ProductPerformance,      |
|    vw_CustomerValue, vw_RegionalPerformance, vw_RFMCustomer,            |
|    vw_CustomerChurn, vw_CLV                                             |
+------------------------------------+------------------------------------+
                                     |
                                     +--------------------+
                                     |                    |
                                     v                    v
+--------------------------------------------+  +-------------------------+
|                  POWER BI                  |  |     MICROSOFT EXCEL     |
|  • 7-Page Executive Dark/Orange Dashboard  |  |  • 7-Sheet Workbook     |
|  • Star Schema DirectQuery / Import Model  |  |  • Native Formulas      |
|  • Centralized _Measures Table (DAX)       |  |  • Pivot Tables & Chart |
|  • Drill-Through, Slicers & Tooltips       |  |  • Supporting Audits    |
+--------------------------------------------+  +-------------------------+
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Raw Ingestion & Synthetic Generation
- **Role**: Emulates realistic enterprise e-commerce transactional event streams across 4 continuous operational years (2022 to 2025).
- **Scale**:
  - `Customers`: 100,000+ unique demographic and regional accounts.
  - `Products`: 2,000+ SKUs across 10 merchandise categories with category-specific cost and retail margin targets.
  - `Orders`: 500,000+ order headers featuring Q4 holiday shopping spikes (Black Friday, Cyber Monday, Christmas).
  - `Sales`: 2,000,000+ individual line items.
  - `Returns`: Category-weighted returns (apparel size issues, electronics quality defects, etc.).
- **Reproducibility**: Parameterized with a fixed random seed (`42`).

### Layer 2: Automated Data Cleaning & Quality Assurance
- **Deduplication**: Identifies and eliminates redundant keys.
- **Referential Integrity**: Guarantees zero orphan keys between Sales, Orders, Products, and Customers.
- **Mathematical Integrity**: Verifies exact penny-level mathematical identity:
  $$\text{SalesAmount} = \text{Quantity} \times \text{UnitPrice} - \text{DiscountAmount}$$
  $$\text{ProfitAmount} = \text{SalesAmount} - \text{CostAmount}$$
- **Chronological Coherence**: Enforces strict temporal ordering (`SignupDate <= OrderDate <= ShippingDate <= DeliveryDate <= ReturnDate`).

### Layer 3: SQL Server Staging (`stg`)
- **Role**: High-speed, unindexed landing zone mimicking operational staging lakes.
- **Tables**: `stg.Customers`, `stg.Products`, `stg.Orders`, `stg.Sales`, `stg.Returns`.
- **Loading Technique**: Optimized using SQLAlchemy with `fast_executemany=True` and T-SQL `BULK INSERT` with `TABLOCK`.

### Layer 4: Data Warehouse Star Schema (`dw`)
- **Role**: Dimensional data model optimized for online analytical processing (OLAP) and BI tools.
- **Surrogate Keys**: Auto-incrementing integer surrogate keys decouple DW dimensions from source operational systems.
- **Indexing Strategy**:
  - B-tree indexes on foreign keys to accelerate relational join filtering.
  - **Nonclustered Columnstore Index (NCCI)** on `FactSales` compressing 2M+ rows in memory and delivering 10x-50x speedups on multi-dimensional aggregations.

### Layer 5: Analytical Views (`analytics`)
- **Role**: Encapsulates business logic, window functions, and multi-table joins into pre-defined database views.
- **Benefit**: Simplifies downstream report building in Power BI and protects client tools from underlying schema changes.

### Layer 6: Presentation Tier (Power BI & Microsoft Excel)
- **Power BI**: Primary executive business intelligence application delivering interactive slicing, time intelligence, cohort tracking, and drill-through.
- **Microsoft Excel**: Analyst workbench providing financial modeling, `XLOOKUP` validation, pivot tables, and data dictionaries.
