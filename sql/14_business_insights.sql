-- ============================================================================
-- SCRIPT: 14_business_insights.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Structured SQL queries directly answering all 33 Core Business Questions.
-- ============================================================================

USE VeyraDW;
GO

PRINT '====================================================================';
PRINT '  VEYRA 33 CORE BUSINESS QUESTIONS — ANALYTICAL QUERY SUITE';
PRINT '====================================================================';

-- ----------------------------------------------------------------------------
-- SALES QUESTIONS (1 - 11)
-- ----------------------------------------------------------------------------

-- Q1: What is Veyra's total revenue?
-- Q2: What is total profit?
-- Q9: What is the average order value (AOV)?
-- Q11: How much revenue comes from discounts?
SELECT 
    SUM(SalesAmount) AS TotalRevenue,                                -- Q1
    SUM(ProfitAmount) AS TotalProfit,                                 -- Q2
    ROUND(SUM(ProfitAmount) / NULLIF(SUM(SalesAmount), 0) * 100, 2) AS ProfitMarginPercent,
    ROUND(SUM(SalesAmount) / NULLIF(COUNT(DISTINCT OrderID), 0), 2) AS AverageOrderValue, -- Q9
    SUM(DiscountAmount) AS TotalDiscountAmount                        -- Q11
FROM dw.FactSales;

-- Q3: What is the monthly revenue trend?
-- Q4: What is the year-over-year growth?
-- Q5: Which months have the highest sales?
WITH MonthlyStats AS (
    SELECT 
        d.Year,
        d.Month,
        d.MonthName,
        SUM(f.SalesAmount) AS MonthlyRevenue,
        RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS SalesRankInHistory
    FROM dw.FactSales f
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY d.Year, d.Month, d.MonthName
)
SELECT 
    Year, Month, MonthName, MonthlyRevenue,
    LAG(MonthlyRevenue, 12) OVER (ORDER BY Year * 100 + Month) AS PriorYearSameMonthRevenue,
    ROUND((MonthlyRevenue - LAG(MonthlyRevenue, 12) OVER (ORDER BY Year * 100 + Month)) 
          / NULLIF(LAG(MonthlyRevenue, 12) OVER (ORDER BY Year * 100 + Month), 0) * 100, 2) AS YoY_Growth_Percent,
    SalesRankInHistory
FROM MonthlyStats
ORDER BY Year, Month;

-- Q6: Which categories generate the most revenue?
-- Q26: Which categories have the highest profit margin?
SELECT 
    dp.CategoryName,
    SUM(f.SalesAmount) AS TotalRevenue,                               -- Q6
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS ProfitMarginPercent, -- Q26
    DENSE_RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS RevenueRank,
    DENSE_RANK() OVER (ORDER BY SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) DESC) AS MarginRank
FROM dw.FactSales f
INNER JOIN dw.DimProduct dp ON f.ProductKey = dp.ProductKey
GROUP BY dp.CategoryName
ORDER BY TotalRevenue DESC;

-- Q7: Which products generate the most revenue?
-- Q8: Which products generate the most profit?
-- Q24: Which products sell the most units?
SELECT TOP 10
    dp.ProductID,
    dp.ProductName,
    dp.CategoryName,
    SUM(f.Quantity) AS UnitsSold,                                     -- Q24
    SUM(f.SalesAmount) AS TotalRevenue,                               -- Q7
    SUM(f.ProfitAmount) AS TotalProfit,                               -- Q8
    DENSE_RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS RevenueRank,
    DENSE_RANK() OVER (ORDER BY SUM(f.ProfitAmount) DESC) AS ProfitRank,
    DENSE_RANK() OVER (ORDER BY SUM(f.Quantity) DESC) AS UnitsRank
FROM dw.FactSales f
INNER JOIN dw.DimProduct dp ON f.ProductKey = dp.ProductKey
GROUP BY dp.ProductID, dp.ProductName, dp.CategoryName
ORDER BY TotalRevenue DESC;

-- Q10: What is the return rate?
SELECT 
    (SELECT COUNT(*) FROM dw.FactReturns) AS TotalReturnedItems,
    (SELECT COUNT(*) FROM dw.FactSales) AS TotalSoldLines,
    ROUND(CAST((SELECT COUNT(*) FROM dw.FactReturns) AS FLOAT) / 
          NULLIF((SELECT COUNT(*) FROM dw.FactSales), 0) * 100, 2) AS OverallReturnRatePercent; -- Q10

-- ----------------------------------------------------------------------------
-- CUSTOMER QUESTIONS (12 - 19)
-- ----------------------------------------------------------------------------

-- Q12: How many customers does Veyra have?
-- Q13: How many are new vs returning?
-- Q14: What percentage of customers are repeat customers?
WITH CustOrders AS (
    SELECT dc.CustomerKey, COUNT(DISTINCT f.OrderID) AS OrderCount
    FROM dw.DimCustomer dc
    LEFT JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    GROUP BY dc.CustomerKey
)
SELECT 
    COUNT(CustomerKey) AS TotalCustomers,                             -- Q12
    SUM(CASE WHEN OrderCount = 1 THEN 1 ELSE 0 END) AS OneTimeCustomers, -- Q13
    SUM(CASE WHEN OrderCount > 1 THEN 1 ELSE 0 END) AS RepeatCustomers,  -- Q13
    ROUND(CAST(SUM(CASE WHEN OrderCount > 1 THEN 1 ELSE 0 END) AS FLOAT) / 
          NULLIF(COUNT(CustomerKey), 0) * 100, 2) AS RepeatCustomerPercentage -- Q14
FROM CustOrders;

-- Q15: Which customers generate the most revenue?
-- Q16: Which customers generate the most profit?
SELECT TOP 10
    dc.CustomerID,
    dc.CustomerName,
    dc.Country,
    SUM(f.SalesAmount) AS TotalRevenue,                               -- Q15
    SUM(f.ProfitAmount) AS TotalProfit,                               -- Q16
    COUNT(DISTINCT f.OrderID) AS OrderCount
FROM dw.DimCustomer dc
INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
GROUP BY dc.CustomerID, dc.CustomerName, dc.Country
ORDER BY TotalRevenue DESC;

-- Q17: Which customer segments are most valuable?
-- Q18: Which customers are at risk of churn?
-- Q19: What is the estimated customer lifetime value?
-- (See Script 11, 12, 13 and Views for detailed segmentation, churn and CLV queries)

-- ----------------------------------------------------------------------------
-- REGIONAL QUESTIONS (20 - 23)
-- ----------------------------------------------------------------------------

-- Q20: Which countries generate the most revenue?
-- Q21: Which regions perform best?
-- Q23: Which regions have the highest profit margin?
SELECT 
    dl.Region,                                                        -- Q21
    dl.Country,                                                       -- Q20
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS RegionProfitMargin -- Q23
FROM dw.FactSales f
INNER JOIN dw.DimLocation dl ON f.LocationKey = dl.LocationKey
GROUP BY dl.Region, dl.Country
ORDER BY TotalRevenue DESC;

-- Q22: Which cities generate the most orders?
SELECT TOP 10
    dl.City,
    dl.Country,
    dl.Region,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,                         -- Q22
    SUM(f.SalesAmount) AS CityRevenue
FROM dw.FactSales f
INNER JOIN dw.DimLocation dl ON f.LocationKey = dl.LocationKey
GROUP BY dl.City, dl.Country, dl.Region
ORDER BY TotalOrders DESC;

-- ----------------------------------------------------------------------------
-- PRODUCT QUESTIONS (24 - 27)
-- ----------------------------------------------------------------------------

-- Q25: Which products have the highest return rate?
WITH Sold AS (
    SELECT dp.ProductID, dp.ProductName, SUM(f.Quantity) AS UnitsSold
    FROM dw.DimProduct dp
    INNER JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
    GROUP BY dp.ProductID, dp.ProductName
),
Ret AS (
    SELECT dp.ProductID, SUM(r.QuantityReturned) AS UnitsRet
    FROM dw.DimProduct dp
    INNER JOIN dw.FactReturns r ON dp.ProductKey = r.ProductKey
    GROUP BY dp.ProductID
)
SELECT TOP 10
    s.ProductID, s.ProductName, s.UnitsSold, ISNULL(r.UnitsRet, 0) AS UnitsReturned,
    ROUND(CAST(ISNULL(r.UnitsRet, 0) AS FLOAT) / NULLIF(s.UnitsSold, 0) * 100, 2) AS ReturnRatePercent -- Q25
FROM Sold s
LEFT JOIN Ret r ON s.ProductID = r.ProductID
WHERE s.UnitsSold >= 250
ORDER BY ReturnRatePercent DESC;

-- Q27: Which products are underperforming?
SELECT TOP 10
    dp.ProductID, dp.ProductName, dp.CategoryName,
    SUM(f.Quantity) AS UnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue                                -- Q27
FROM dw.DimProduct dp
INNER JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
GROUP BY dp.ProductID, dp.ProductName, dp.CategoryName
ORDER BY UnitsSold ASC, TotalRevenue ASC;
GO
