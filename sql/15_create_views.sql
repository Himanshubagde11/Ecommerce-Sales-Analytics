-- ============================================================================
-- SCRIPT: 15_create_views.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates 8 production-grade analytical views in schema [analytics]
--              optimized for DirectQuery and Import models in Microsoft Power BI.
-- ============================================================================

USE VeyraDW;
GO

-- 1. analytics.vw_MonthlySales
IF OBJECT_ID('analytics.vw_MonthlySales', 'V') IS NOT NULL DROP VIEW analytics.vw_MonthlySales;
GO
CREATE VIEW analytics.vw_MonthlySales AS
SELECT 
    d.Year,
    d.Quarter,
    d.QuarterName,
    d.Month,
    d.MonthName,
    d.Year * 100 + d.Month AS YearMonthKey,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalUnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.CostAmount) AS TotalCost,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS ProfitMarginPercent,
    ROUND(SUM(f.SalesAmount) / NULLIF(COUNT(DISTINCT f.OrderID), 0), 2) AS AverageOrderValue,
    SUM(f.DiscountAmount) AS TotalDiscounts
FROM dw.FactSales f
INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
GROUP BY d.Year, d.Quarter, d.QuarterName, d.Month, d.MonthName, d.Year * 100 + d.Month;
GO

-- 2. analytics.vw_CategoryPerformance
IF OBJECT_ID('analytics.vw_CategoryPerformance', 'V') IS NOT NULL DROP VIEW analytics.vw_CategoryPerformance;
GO
CREATE VIEW analytics.vw_CategoryPerformance AS
SELECT 
    dp.CategoryID,
    dp.CategoryName,
    COUNT(DISTINCT dp.ProductID) AS ActiveProducts,
    SUM(f.Quantity) AS TotalUnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.CostAmount) AS TotalCost,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS ProfitMarginPercent,
    ROUND(SUM(f.SalesAmount) / SUM(SUM(f.SalesAmount)) OVER () * 100, 2) AS RevenueContributionPercent
FROM dw.FactSales f
INNER JOIN dw.DimProduct dp ON f.ProductKey = dp.ProductKey
GROUP BY dp.CategoryID, dp.CategoryName;
GO

-- 3. analytics.vw_ProductPerformance
IF OBJECT_ID('analytics.vw_ProductPerformance', 'V') IS NOT NULL DROP VIEW analytics.vw_ProductPerformance;
GO
CREATE VIEW analytics.vw_ProductPerformance AS
SELECT 
    dp.ProductID,
    dp.ProductName,
    dp.Brand,
    dp.CategoryID,
    dp.CategoryName,
    dp.UnitCost,
    dp.UnitPrice,
    SUM(f.Quantity) AS UnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.CostAmount) AS TotalCost,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS GrossMarginPercent
FROM dw.FactSales f
INNER JOIN dw.DimProduct dp ON f.ProductKey = dp.ProductKey
GROUP BY dp.ProductID, dp.ProductName, dp.Brand, dp.CategoryID, dp.CategoryName, dp.UnitCost, dp.UnitPrice;
GO

-- 4. analytics.vw_CustomerValue
IF OBJECT_ID('analytics.vw_CustomerValue', 'V') IS NOT NULL DROP VIEW analytics.vw_CustomerValue;
GO
CREATE VIEW analytics.vw_CustomerValue AS
SELECT 
    dc.CustomerKey,
    dc.CustomerID,
    dc.CustomerName,
    dc.Gender,
    dc.Age,
    dc.Country,
    dc.Region,
    dc.AcquisitionChannel,
    dc.SignupDate,
    COUNT(DISTINCT f.OrderID) AS LifetimeOrders,
    SUM(f.Quantity) AS LifetimeUnitsPurchased,
    SUM(f.SalesAmount) AS LifetimeRevenue,
    SUM(f.ProfitAmount) AS LifetimeProfit,
    ROUND(SUM(f.SalesAmount) / NULLIF(COUNT(DISTINCT f.OrderID), 0), 2) AS AverageOrderValue,
    MIN(d.FullDate) AS FirstPurchaseDate,
    MAX(d.FullDate) AS LastPurchaseDate
FROM dw.DimCustomer dc
LEFT JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
LEFT JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.Gender, dc.Age, dc.Country, dc.Region, dc.AcquisitionChannel, dc.SignupDate;
GO

-- 5. analytics.vw_RegionalPerformance
IF OBJECT_ID('analytics.vw_RegionalPerformance', 'V') IS NOT NULL DROP VIEW analytics.vw_RegionalPerformance;
GO
CREATE VIEW analytics.vw_RegionalPerformance AS
SELECT 
    dl.Region,
    dl.Country,
    dl.State,
    dl.City,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    COUNT(DISTINCT f.CustomerKey) AS UniqueBuyers,
    SUM(f.Quantity) AS TotalUnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS ProfitMarginPercent,
    ROUND(SUM(f.SalesAmount) / NULLIF(COUNT(DISTINCT f.OrderID), 0), 2) AS AverageOrderValue
FROM dw.FactSales f
INNER JOIN dw.DimLocation dl ON f.LocationKey = dl.LocationKey
GROUP BY dl.Region, dl.Country, dl.State, dl.City;
GO

-- 6. analytics.vw_RFMCustomer
IF OBJECT_ID('analytics.vw_RFMCustomer', 'V') IS NOT NULL DROP VIEW analytics.vw_RFMCustomer;
GO
CREATE VIEW analytics.vw_RFMCustomer AS
WITH MaxDate AS (
    SELECT DATEADD(DAY, 1, MAX(FullDate)) AS RefDate FROM dw.DimDate WHERE DateKey IN (SELECT DISTINCT OrderDateKey FROM dw.FactSales)
),
CustMetrics AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.Country,
        dc.Region,
        DATEDIFF(DAY, MAX(d.FullDate), (SELECT RefDate FROM MaxDate)) AS Recency,
        COUNT(DISTINCT f.OrderID) AS Frequency,
        SUM(f.SalesAmount) AS Monetary
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.Country, dc.Region
),
CustScores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY Recency DESC) AS R_Score,
        NTILE(5) OVER (ORDER BY Frequency ASC) AS F_Score,
        NTILE(5) OVER (ORDER BY Monetary ASC) AS M_Score
    FROM CustMetrics
)
SELECT 
    CustomerKey,
    CustomerID,
    CustomerName,
    Country,
    Region,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    CAST(R_Score AS VARCHAR(1)) + CAST(F_Score AS VARCHAR(1)) + CAST(M_Score AS VARCHAR(1)) AS RFM_Score,
    CASE 
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
        WHEN R_Score <= 2 AND F_Score >= 4 AND M_Score >= 4 THEN 'Cannot Lose Them'
        WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Risk'
        WHEN R_Score >= 4 AND F_Score IN (2, 3) THEN 'Potential Loyalists'
        WHEN R_Score >= 4 AND F_Score = 1 THEN 'New Customers'
        WHEN R_Score = 3 AND F_Score = 1 THEN 'Promising'
        WHEN R_Score IN (2, 3) AND F_Score IN (2, 3) THEN 'Need Attention'
        WHEN R_Score <= 2 AND F_Score <= 2 THEN 'Lost Customers'
        ELSE 'Need Attention'
    END AS RFM_Segment
FROM CustScores;
GO

-- 7. analytics.vw_CustomerChurn
IF OBJECT_ID('analytics.vw_CustomerChurn', 'V') IS NOT NULL DROP VIEW analytics.vw_CustomerChurn;
GO
CREATE VIEW analytics.vw_CustomerChurn AS
WITH MaxDate AS (
    SELECT DATEADD(DAY, 1, MAX(FullDate)) AS RefDate FROM dw.DimDate WHERE DateKey IN (SELECT DISTINCT OrderDateKey FROM dw.FactSales)
),
CustomerBase AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.Country,
        dc.Region,
        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.SalesAmount) AS TotalRevenue,
        DATEDIFF(DAY, MAX(d.FullDate), (SELECT RefDate FROM MaxDate)) AS DaysSinceLastPurchase,
        DATEDIFF(DAY, MIN(d.FullDate), MAX(d.FullDate)) AS CustomerLifespanDays
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.Country, dc.Region
),
Intervals AS (
    SELECT 
        *,
        CASE 
            WHEN TotalOrders > 1 THEN 
                CASE 
                    WHEN CustomerLifespanDays / (TotalOrders - 1) < 7 THEN 7 
                    ELSE CustomerLifespanDays / (TotalOrders - 1) 
                END
            ELSE NULL 
        END AS AvgInterPurchaseDays
    FROM CustomerBase
)
SELECT 
    CustomerKey,
    CustomerID,
    CustomerName,
    Country,
    Region,
    TotalOrders,
    TotalRevenue,
    DaysSinceLastPurchase,
    CustomerLifespanDays,
    AvgInterPurchaseDays,
    CASE 
        WHEN TotalOrders = 1 THEN
            CASE 
                WHEN DaysSinceLastPurchase <= 90 THEN 'Low Risk'
                WHEN DaysSinceLastPurchase <= 270 THEN 'Medium Risk'
                ELSE 'High Risk'
            END
        ELSE
            CASE 
                WHEN DaysSinceLastPurchase <= 1.5 * AvgInterPurchaseDays THEN 'Low Risk'
                WHEN DaysSinceLastPurchase <= 3.0 * AvgInterPurchaseDays AND DaysSinceLastPurchase <= 365 THEN 'Medium Risk'
                ELSE 'High Risk'
            END
    END AS ChurnRisk,
    CASE 
        WHEN TotalOrders = 1 AND DaysSinceLastPurchase > 270 THEN TotalRevenue
        WHEN TotalOrders > 1 AND (DaysSinceLastPurchase > 3.0 * AvgInterPurchaseDays OR DaysSinceLastPurchase > 365) THEN TotalRevenue
        ELSE 0.0
    END AS RevenueAtRisk
FROM Intervals;
GO

-- 8. analytics.vw_CLV
IF OBJECT_ID('analytics.vw_CLV', 'V') IS NOT NULL DROP VIEW analytics.vw_CLV;
GO
CREATE VIEW analytics.vw_CLV AS
WITH CustomerAgg AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.AcquisitionChannel,
        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.SalesAmount) AS TotalRevenue,
        SUM(f.ProfitAmount) AS TotalProfit
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.AcquisitionChannel
)
SELECT 
    CustomerKey,
    CustomerID,
    CustomerName,
    AcquisitionChannel,
    TotalOrders,
    TotalRevenue,
    TotalProfit,
    ROUND(TotalRevenue / NULLIF(TotalOrders, 0), 2) AS AverageOrderValue,
    ROUND(TotalProfit / NULLIF(TotalRevenue, 0), 4) AS ProfitMarginRate,
    ROUND(CAST(TotalOrders AS FLOAT) / 4.0, 2) AS AnnualPurchaseFrequency,
    ROUND(
        TotalProfit + 
        ((CAST(TotalOrders AS FLOAT) / 4.0) * 
        (TotalRevenue / NULLIF(TotalOrders, 0)) * 
        (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125),
        2
    ) AS EstimatedCLV,
    CASE 
        WHEN (TotalProfit + ((CAST(TotalOrders AS FLOAT) / 4.0) * (TotalRevenue / NULLIF(TotalOrders, 0)) * (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125)) >= 2500 THEN 'Platinum VIP'
        WHEN (TotalProfit + ((CAST(TotalOrders AS FLOAT) / 4.0) * (TotalRevenue / NULLIF(TotalOrders, 0)) * (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125)) >= 1000 THEN 'Gold'
        WHEN (TotalProfit + ((CAST(TotalOrders AS FLOAT) / 4.0) * (TotalRevenue / NULLIF(TotalOrders, 0)) * (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125)) >= 400 THEN 'Silver'
        ELSE 'Bronze'
    END AS CLV_Segment
FROM CustomerAgg;
GO

PRINT 'All 8 Power BI Analytics Views created successfully.';
GO
