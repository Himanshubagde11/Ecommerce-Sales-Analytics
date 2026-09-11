# VEYRA Enterprise Data Warehouse: Data Dictionary

Comprehensive data dictionary documenting every dimension, fact, attribute, data type, and business calculation within `VeyraDW`.

---

## 1. Dimension Tables

### `dw.DimCustomer`
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CustomerKey` | `dw.DimCustomer` | `INT (PK)` | Auto-incrementing surrogate primary key | Unique warehouse customer ID | `10482` |
| `CustomerID` | `dw.DimCustomer` | `INT` | Natural source customer account number | Originating store profile ID | `10482` |
| `CustomerName` | `dw.DimCustomer` | `VARCHAR(150)` | Full legal name of customer | Customer display name | `Sophia Miller` |
| `Gender` | `dw.DimCustomer` | `VARCHAR(20)` | Customer stated gender identity | Demographic segmentation | `Female` |
| `Age` | `dw.DimCustomer` | `INT` | Customer age in completed years | Generational cohorting | `34` |
| `SignupDate` | `dw.DimCustomer` | `DATE` | Account creation timestamp | Customer tenure baseline | `2022-03-15` |
| `Email` | `dw.DimCustomer` | `VARCHAR(150)` | Contact email address | Direct CRM outreach | `sophia.miller.10482@gmail.com` |
| `City` | `dw.DimCustomer` | `VARCHAR(100)` | Residential city | Urban market analysis | `Chicago` |
| `State` | `dw.DimCustomer` | `VARCHAR(100)` | State, province, or department | Sub-national logistics | `Illinois` |
| `Country` | `dw.DimCustomer` | `VARCHAR(100)` | Country of residence | National legal territory | `United States` |
| `Region` | `dw.DimCustomer` | `VARCHAR(50)` | Global geographic theater | Strategic market theater | `North America` |
| `AcquisitionChannel` | `dw.DimCustomer` | `VARCHAR(50)` | First-touch attribution marketing source | Channel acquisition CAC/ROAS | `Paid Search` |

### `dw.DimProduct`
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ProductKey` | `dw.DimProduct` | `INT (PK)` | Auto-incrementing surrogate primary key | Warehouse product identifier | `481` |
| `ProductID` | `dw.DimProduct` | `INT` | Natural catalog product SKU ID | Commercial catalog code | `481` |
| `ProductName` | `dw.DimProduct` | `VARCHAR(200)` | Title, model, and specification | Merchandising display title | `Sony 4K OLED Monitor Pro` |
| `Brand` | `dw.DimProduct` | `VARCHAR(100)` | Manufacturing or merchant brand | Vendor partner attribution | `Sony` |
| `CategoryID` | `dw.DimProduct` | `INT (FK)` | Links to `DimCategory` | Department taxonomy | `1` |
| `CategoryName` | `dw.DimProduct` | `VARCHAR(50)` | Retail category label | High-level merchandising group | `Electronics` |
| `UnitCost` | `dw.DimProduct` | `DECIMAL(18,2)`| Procurement cost per unit in USD | Direct product inventory cost | `245.00` |
| `UnitPrice` | `dw.DimProduct` | `DECIMAL(18,2)`| Base list retail price in USD | Manufacturer suggested price | `349.99` |
| `ProductLaunchDate` | `dw.DimProduct` | `DATE` | Date SKU launched on storefront | Product lifecycle maturity | `2021-08-10` |

### `dw.DimCategory`
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CategoryID` | `dw.DimCategory` | `INT (PK)` | Numerical category key | Department code | `2` |
| `CategoryName` | `dw.DimCategory` | `VARCHAR(50)` | Primary retail category name | Merchandising department | `Fashion` |
| `Description` | `dw.DimCategory` | `VARCHAR(250)`| Department description | Categorical scope | `Apparel and clothing` |

### `dw.DimDate`
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DateKey` | `dw.DimDate` | `INT (PK)` | Integer date key formatted as YYYYMMDD | Fast relational calendar join | `20231124` |
| `FullDate` | `dw.DimDate` | `DATE` | Standard calendar date | Temporal slicing | `2023-11-24` |
| `Year` | `dw.DimDate` | `INT` | 4-digit calendar year | Annual reporting | `2023` |
| `Quarter` | `dw.DimDate` | `INT` | Calendar quarter (1 to 4) | Quarterly performance cycles | `4` |
| `Month` | `dw.DimDate` | `INT` | Month number (1 to 12) | Monthly periodicity | `11` |
| `MonthName` | `dw.DimDate` | `VARCHAR(20)` | Full English month name | Visual axis labeling | `November` |
| `DayOfWeek` | `dw.DimDate` | `INT` | Day of week integer (1=Sun to 7=Sat) | Weekly trend modeling | `6` |
| `IsWeekend` | `dw.DimDate` | `BIT` | Flag indicating Saturday or Sunday | Weekend shopping surge | `0` |
| `IsHolidaySeason` | `dw.DimDate` | `BIT` | Flag indicating November or December | Q4 holiday retail surge | `1` |

---

## 2. Fact Tables

### `dw.FactSales` (2,000,000+ Records)
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SalesKey` | `dw.FactSales` | `BIGINT (PK)` | Surrogate key for order-line record | Unique transaction row | `1849204` |
| `SalesID` | `dw.FactSales` | `INT` | Natural order line item number | Line item index | `1849204` |
| `OrderID` | `dw.FactSales` | `INT` | Order basket header reference | Transaction grouping | `429103` |
| `CustomerKey` | `dw.FactSales` | `INT (FK)` | Foreign key to `DimCustomer` | Customer purchasing the item | `10482` |
| `ProductKey` | `dw.FactSales` | `INT (FK)` | Foreign key to `DimProduct` | Product purchased | `481` |
| `OrderDateKey` | `dw.FactSales` | `INT (FK)` | Foreign key to `DimDate` | Date order was placed | `20231124` |
| `LocationKey` | `dw.FactSales` | `INT (FK)` | Foreign key to `DimLocation` | Shipping destination | `14` |
| `PaymentKey` | `dw.FactSales` | `INT (FK)` | Foreign key to `DimPayment` | Settlement instrument | `1` |
| `OrderStatus` | `dw.FactSales` | `VARCHAR(30)` | Status: Delivered, Cancelled, Returned, Pending | Fulfillment lifecycle stage | `Delivered` |
| `Quantity` | `dw.FactSales` | `INT` | Number of units ordered in line | Item purchase volume | `2` |
| `UnitPrice` | `dw.FactSales` | `DECIMAL(18,2)`| Base list unit price at transaction | Gross catalogue price | `349.99` |
| `DiscountAmount` | `dw.FactSales` | `DECIMAL(18,2)`| Total promotional discount on line | Promotional concession | `35.00` |
| `SalesAmount` | `dw.FactSales` | `DECIMAL(18,2)`| Net revenue: Quantity * UnitPrice - Discount | Net revenue recognized | `664.98` |
| `CostAmount` | `dw.FactSales` | `DECIMAL(18,2)`| Total product cost: Quantity * UnitCost | Cost of goods sold (COGS) | `490.00` |
| `ProfitAmount` | `dw.FactSales` | `DECIMAL(18,2)`| Gross profit: SalesAmount - CostAmount | Operating contribution margin | `174.98` |

### `dw.FactReturns`
| Field | Table | Data Type | Description | Business Meaning | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ReturnKey` | `dw.FactReturns` | `BIGINT (PK)` | Auto-incrementing return surrogate key | Unique merchandise return | `14820` |
| `ReturnID` | `dw.FactReturns` | `INT` | Natural return authorization code | RMA incident ID | `14820` |
| `OrderID` | `dw.FactReturns` | `INT` | Associated original order ID | Originating order | `429103` |
| `CustomerKey` | `dw.FactReturns` | `INT (FK)` | Foreign key to `DimCustomer` | Returning customer | `10482` |
| `ProductKey` | `dw.FactReturns` | `INT (FK)` | Foreign key to `DimProduct` | Returned product | `481` |
| `ReturnDateKey` | `dw.FactReturns` | `INT (FK)` | Foreign key to `DimDate` | Date return received | `20231205` |
| `QuantityReturned`| `dw.FactReturns` | `INT` | Units returned back to inventory | Inventory restock count | `1` |
| `ReturnAmount` | `dw.FactReturns` | `DECIMAL(18,2)`| Refund value credited to customer | Revenue reversal | `332.49` |
| `ReturnReason` | `dw.FactReturns` | `VARCHAR(100)`| Categorized reason for return | Quality and sizing diagnostics | `Size Issue` |
