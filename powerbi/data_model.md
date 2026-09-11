# Power BI Data Model Architecture: VEYRA E-Commerce

## 1. Dimensional Star Schema Architecture

The Veyra Power BI data model adheres to industry-standard Kimball Star Schema principles. The data warehouse centralizes enterprise order-line transactions in `FactSales` (2M+ grain) and merchandise returns in `FactReturns`, surrounded by conformist dimension tables.

```
       +-------------------+       +-------------------+
       |    DimCustomer    |       |     DimProduct    |
       +-------------------+       +-------------------+
       | CustomerKey (PK)  |       | ProductKey (PK)   |
       | CustomerID        |       | ProductID         |
       | CustomerName      |       | ProductName       |
       | Country, Region   |       | Brand             |
       | AcquisitionChannel|       | CategoryName      |
       +---------+---------+       +---------+---------+
                 |                           |
                 | (1:*)                     | (1:*)
                 |                           |
                 v                           v
       +-----------------------------------------------+
       |                   FactSales                   |
       +-----------------------------------------------+
       | SalesKey (PK)                                 |
       | OrderID                                       |
       | CustomerKey (FK)                              |
       | ProductKey (FK)                               |
       | OrderDateKey (FK)                             |
       | LocationKey (FK)                              |
       | PaymentKey (FK)                               |
       | Quantity                                      |
       | UnitPrice, DiscountAmount                     |
       | SalesAmount, CostAmount, ProfitAmount         |
       +---+--------------------+------------------+---+
           |                    |                  |
     (1:*) |              (1:*) |            (1:*) |
           v                    v                  v
+------------------+  +------------------+  +------------------+
|     DimDate      |  |   DimLocation    |  |    DimPayment    |
+------------------+  +------------------+  +------------------+
| DateKey (PK)     |  | LocationKey (PK) |  | PaymentKey (PK)  |
| FullDate         |  | City             |  | PaymentMethod    |
| Year, Quarter    |  | State            |  +------------------+
| Month, MonthName |  | Country          |
| IsWeekend        |  | Region           |
| IsHolidaySeason  |  +------------------+
+------------------+
```

---

## 2. Model Relationships & Cardinalities

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter Direction | Active | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dw.FactSales` | `CustomerKey` | `dw.DimCustomer` | `CustomerKey` | Many to One (*:1) | Single | **Yes** | Filters sales by customer attributes |
| `dw.FactSales` | `ProductKey` | `dw.DimProduct` | `ProductKey` | Many to One (*:1) | Single | **Yes** | Filters sales by product/brand/category |
| `dw.FactSales` | `OrderDateKey` | `dw.DimDate` | `DateKey` | Many to One (*:1) | Single | **Yes** | Primary transactional calendar filtering |
| `dw.FactSales` | `LocationKey` | `dw.DimLocation` | `LocationKey` | Many to One (*:1) | Single | **Yes** | Geographic slicing and drill-down |
| `dw.FactSales` | `PaymentKey` | `dw.DimPayment` | `PaymentKey` | Many to One (*:1) | Single | **Yes** | Slicing by payment instrument |
| `dw.FactReturns` | `CustomerKey` | `dw.DimCustomer` | `CustomerKey` | Many to One (*:1) | Single | **Yes** | Evaluates customer-specific return behavior |
| `dw.FactReturns` | `ProductKey` | `dw.DimProduct` | `ProductKey` | Many to One (*:1) | Single | **Yes** | Evaluates product return rates and defects |
| `dw.FactReturns` | `ReturnDateKey`| `dw.DimDate` | `DateKey` | Many to One (*:1) | Single | **Yes** | Slices returns by calendar date |

---

## 3. Analytical Presentation Views

When connecting Power BI to SQL Server, analysts can ingest either the core Star Schema tables (`dw.FactSales`, `dw.Dim*`) for granular drill-through, or the pre-aggregated analytical views from the `analytics` schema:

1. `analytics.vw_MonthlySales`: Pre-aggregated monthly revenue, profit, unit sales, and discounts.
2. `analytics.vw_CategoryPerformance`: Category-level gross margin and revenue shares.
3. `analytics.vw_ProductPerformance`: Catalog product margins, units, and brand sales.
4. `analytics.vw_CustomerValue`: Customer-level lifetime spend, order frequency, and recency.
5. `analytics.vw_RegionalPerformance`: Hierarchical geographic sales (Region -> Country -> State -> City).
6. `analytics.vw_RFMCustomer`: Pre-scored 1-5 quintiles and assigned RFM segments.
7. `analytics.vw_CustomerChurn`: Behavioral churn risk tiers (Low, Medium, High) and Revenue at Risk.
8. `analytics.vw_CLV`: Documented Customer Lifetime Value projections and VIP tiers.

---

## 4. Modeling Best Practices Implemented
- **Single-Direction Filtering**: Enforces deterministic query paths and prevents ambiguous circular relationships.
- **Dedicated Measures Table**: All business metrics are maintained in `_Measures` rather than scattered across tables.
- **Surrogate Keys**: Integer surrogate keys (`CustomerKey`, `ProductKey`, `DateKey`) ensure optimal memory compression in VertiPaq.
- **Date Dimension Alignment**: `DimDate[FullDate]` is marked as the official Date Table in Power BI to ensure time-intelligence DAX functions work reliably.
