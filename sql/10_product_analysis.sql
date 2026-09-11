-- ============================================================================
-- SCRIPT: 10_product_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Product performance, return rates, brand analysis, and margin
--              rankings using window functions and CTEs.
-- ============================================================================

USE VeyraDW;
GO

-- 1. Top 20 Best-Selling Products by Revenue & Profit
WITH ProductPerformance AS (
    SELECT 
        dp.ProductID,
        dp.ProductName,
        dp.Brand,
        dp.CategoryName,
        dp.UnitPrice,
        dp.UnitCost,
        SUM(f.Quantity) AS UnitsSold,
        SUM(f.SalesAmount) AS TotalRevenue,
        SUM(f.ProfitAmount) AS TotalProfit,
        ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS GrossMarginPercent
    FROM dw.DimProduct dp
    INNER JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
    GROUP BY dp.ProductID, dp.ProductName, dp.Brand, dp.CategoryName, dp.UnitPrice, dp.UnitCost
)
SELECT TOP 20
    ProductID,
    ProductName,
    Brand,
    CategoryName,
    UnitPrice,
    UnitsSold,
    TotalRevenue,
    TotalProfit,
    GrossMarginPercent,
    DENSE_RANK() OVER (ORDER BY TotalRevenue DESC) AS RevenueRank,
    DENSE_RANK() OVER (ORDER BY TotalProfit DESC) AS ProfitRank
FROM ProductPerformance
ORDER BY TotalRevenue DESC;
GO

-- 2. Products with Highest Return Rates (Min 200 units sold)
WITH SalesByProduct AS (
    SELECT 
        dp.ProductID,
        dp.ProductName,
        dp.CategoryName,
        SUM(f.Quantity) AS UnitsSold,
        SUM(f.SalesAmount) AS TotalRevenue
    FROM dw.DimProduct dp
    INNER JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
    GROUP BY dp.ProductID, dp.ProductName, dp.CategoryName
),
ReturnsByProduct AS (
    SELECT 
        dp.ProductID,
        SUM(r.QuantityReturned) AS UnitsReturned,
        SUM(r.ReturnAmount) AS TotalRefundedAmount,
        COUNT(r.ReturnKey) AS ReturnIncidentCount
    FROM dw.DimProduct dp
    INNER JOIN dw.FactReturns r ON dp.ProductKey = r.ProductKey
    GROUP BY dp.ProductID
)
SELECT TOP 20
    s.ProductID,
    s.ProductName,
    s.CategoryName,
    s.UnitsSold,
    ISNULL(r.UnitsReturned, 0) AS UnitsReturned,
    ROUND(CAST(ISNULL(r.UnitsReturned, 0) AS FLOAT) / NULLIF(s.UnitsSold, 0) * 100, 2) AS ReturnRatePercent,
    s.TotalRevenue,
    ISNULL(r.TotalRefundedAmount, 0) AS TotalRefundedAmount
FROM SalesByProduct s
LEFT JOIN ReturnsByProduct r ON s.ProductID = r.ProductID
WHERE s.UnitsSold >= 200
ORDER BY ReturnRatePercent DESC;
GO

-- 3. Top Brands Ranked by Total Revenue and Margin Efficiency
SELECT 
    dp.Brand,
    COUNT(DISTINCT dp.ProductID) AS ProductCount,
    SUM(f.Quantity) AS TotalUnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS BrandMarginPercent,
    DENSE_RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS BrandRevenueRank
FROM dw.DimProduct dp
INNER JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
GROUP BY dp.Brand
ORDER BY TotalRevenue DESC;
GO

-- 4. Underperforming Products (Bottom 20 with Launch Date > 180 Days Ago)
WITH ActiveProducts AS (
    SELECT 
        dp.ProductID,
        dp.ProductName,
        dp.CategoryName,
        dp.ProductLaunchDate,
        ISNULL(SUM(f.Quantity), 0) AS UnitsSold,
        ISNULL(SUM(f.SalesAmount), 0) AS TotalRevenue,
        ISNULL(SUM(f.ProfitAmount), 0) AS TotalProfit
    FROM dw.DimProduct dp
    LEFT JOIN dw.FactSales f ON dp.ProductKey = f.ProductKey
    GROUP BY dp.ProductID, dp.ProductName, dp.CategoryName, dp.ProductLaunchDate
)
SELECT TOP 20
    ProductID,
    ProductName,
    CategoryName,
    ProductLaunchDate,
    UnitsSold,
    TotalRevenue,
    TotalProfit
FROM ActiveProducts
ORDER BY UnitsSold ASC, TotalRevenue ASC;
GO
