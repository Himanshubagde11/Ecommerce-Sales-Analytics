# Power BI DAX Measures Specification: VEYRA E-Commerce

All business metrics are centralized within a dedicated `_Measures` table in Power BI. Every measure follows standard enterprise DAX patterns using `VAR` and `RETURN` constructs for readability, execution plan optimization, and debuggability.

---

## 1. Core Financial & Sales Measures

### Total Revenue
```dax
Total Revenue = 
VAR Result = SUM(FactSales[SalesAmount])
RETURN
    COALESCE(Result, 0)
```
*Format: Currency (`$#,##0`)*

### Total Profit
```dax
Total Profit = 
VAR Result = SUM(FactSales[ProfitAmount])
RETURN
    COALESCE(Result, 0)
```
*Format: Currency (`$#,##0`)*

### Total Cost
```dax
Total Cost = 
VAR Result = SUM(FactSales[CostAmount])
RETURN
    COALESCE(Result, 0)
```
*Format: Currency (`$#,##0`)*

### Gross Profit Margin %
```dax
Profit Margin = 
VAR Revenue = [Total Revenue]
VAR Profit = [Total Profit]
VAR Result = 
    DIVIDE(Profit, Revenue, 0)
RETURN
    Result
```
*Format: Percentage (`0.0%`)*

### Total Orders
```dax
Total Orders = 
VAR Result = DISTINCTCOUNT(FactSales[OrderID])
RETURN
    COALESCE(Result, 0)
```
*Format: Whole Number (`#,##0`)*

### Total Quantity Sold
```dax
Total Quantity = 
VAR Result = SUM(FactSales[Quantity])
RETURN
    COALESCE(Result, 0)
```
*Format: Whole Number (`#,##0`)*

### Average Order Value (AOV)
```dax
Average Order Value = 
VAR Revenue = [Total Revenue]
VAR Orders = [Total Orders]
VAR Result = 
    DIVIDE(Revenue, Orders, 0)
RETURN
    Result
```
*Format: Currency (`$#,##0.00`)*

### Total Discounts Given
```dax
Total Discounts = 
VAR Result = SUM(FactSales[DiscountAmount])
RETURN
    COALESCE(Result, 0)
```
*Format: Currency (`$#,##0`)*

---

## 2. Customer & Retention Measures

### Total Customers
```dax
Total Customers = 
VAR Result = DISTINCTCOUNT(DimCustomer[CustomerKey])
RETURN
    COALESCE(Result, 0)
```
*Format: Whole Number (`#,##0`)*

### Active Purchasing Customers
```dax
Active Purchasing Customers = 
VAR Result = CALCULATE(
    DISTINCTCOUNT(FactSales[CustomerKey]),
    FactSales[SalesAmount] > 0
)
RETURN
    COALESCE(Result, 0)
```
*Format: Whole Number (`#,##0`)*

### Repeat Customer Rate %
```dax
Repeat Customer Rate = 
VAR CustomersWithMultipleOrders = 
    COUNTROWS(
        FILTER(
            VALUES(DimCustomer[CustomerKey]),
            CALCULATE(DISTINCTCOUNT(FactSales[OrderID])) > 1
        )
    )
VAR TotalActiveCustomers = [Active Purchasing Customers]
VAR Result = 
    DIVIDE(CustomersWithMultipleOrders, TotalActiveCustomers, 0)
RETURN
    Result
```
*Format: Percentage (`0.0%`)*

### Average Revenue Per Customer (ARPU)
```dax
Average Revenue Per Customer = 
VAR Revenue = [Total Revenue]
VAR Customers = [Active Purchasing Customers]
VAR Result = 
    DIVIDE(Revenue, Customers, 0)
RETURN
    Result
```
*Format: Currency (`$#,##0.00`)*

---

## 3. Time Intelligence & Growth Measures

### Prior Month Revenue
```dax
Prior Month Revenue = 
VAR Result = 
    CALCULATE(
        [Total Revenue],
        DATEADD(DimDate[FullDate], -1, MONTH)
    )
RETURN
    Result
```
*Format: Currency (`$#,##0`)*

### Month-over-Month (MoM) Revenue Growth %
```dax
MoM Revenue % = 
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue = [Prior Month Revenue]
VAR Result = 
    DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
RETURN
    Result
```
*Format: Percentage (`+0.0%;-0.0%;0.0%`)*

### Prior Year Revenue
```dax
Prior Year Revenue = 
VAR Result = 
    CALCULATE(
        [Total Revenue],
        SAMEPERIODLASTYEAR(DimDate[FullDate])
    )
RETURN
    Result
```
*Format: Currency (`$#,##0`)*

### Year-over-Year (YoY) Revenue Growth %
```dax
YoY Revenue % = 
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue = [Prior Year Revenue]
VAR Result = 
    DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
RETURN
    Result
```
*Format: Percentage (`+0.0%;-0.0%;0.0%`)*

### Year-to-Date (YTD) Revenue
```dax
YTD Revenue = 
VAR Result = 
    TOTALYTD([Total Revenue], DimDate[FullDate])
RETURN
    Result
```
*Format: Currency (`$#,##0`)*

---

## 4. Product, Returns & Churn Measures

### Total Returned Items
```dax
Total Returned Items = 
VAR Result = SUM(FactReturns[QuantityReturned])
RETURN
    COALESCE(Result, 0)
```
*Format: Whole Number (`#,##0`)*

### Return Rate %
```dax
Return Rate = 
VAR ReturnedCount = COUNTROWS(FactReturns)
VAR SalesLineCount = COUNTROWS(FactSales)
VAR Result = 
    DIVIDE(ReturnedCount, SalesLineCount, 0)
RETURN
    Result
```
*Format: Percentage (`0.0%`)*

### Revenue at Risk
```dax
Revenue at Risk = 
VAR HighRiskRevenue = 
    CALCULATE(
        [Total Revenue],
        analytics_vw_CustomerChurn[ChurnRisk] = "High Risk"
    )
RETURN
    COALESCE(HighRiskRevenue, 0)
```
*Format: Currency (`$#,##0`)*

### Estimated CLV
```dax
Estimated CLV = 
VAR AvgAOV = [Average Order Value]
VAR CustOrders = [Total Orders]
VAR MarginRate = [Profit Margin]
VAR ActiveCust = [Active Purchasing Customers]
VAR AnnualOrdersPerCust = DIVIDE(CustOrders, ActiveCust * 4, 0)
VAR FutureHorizonMultiplier = 2.125
VAR ProjectedMargin = AnnualOrdersPerCust * AvgAOV * MarginRate * FutureHorizonMultiplier
VAR HistoricalProfitPerCust = DIVIDE([Total Profit], ActiveCust, 0)
RETURN
    HistoricalProfitPerCust + ProjectedMargin
```
*Format: Currency (`$#,##0.00`)*
