-- ============================================================================
-- SCRIPT: 08_sales_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Core Sales Performance Analytics using Advanced SQL (CTEs,
--              Window Functions, LAG/LEAD, SUM OVER, Date Functions).
-- ============================================================================

USE VeyraDW;
GO

-- 1. Executive Sales KPI Summary
SELECT 
    COUNT(DISTINCT OrderID) AS TotalOrders,
    COUNT(SalesKey) AS TotalSalesLines,
    SUM(Quantity) AS TotalUnitsSold,
    SUM(SalesAmount) AS TotalRevenue,
    SUM(CostAmount) AS TotalCost,
    SUM(ProfitAmount) AS TotalProfit,
    ROUND(SUM(ProfitAmount) / NULLIF(SUM(SalesAmount), 0) * 100, 2) AS GrossProfitMarginPercent,
    ROUND(SUM(SalesAmount) / NULLIF(COUNT(DISTINCT OrderID), 0), 2) AS AverageOrderValue,
    SUM(DiscountAmount) AS TotalDiscountsGiven
FROM dw.FactSales;
GO

-- 2. Monthly Revenue Trend with MoM Growth % using CTE and LAG()
WITH MonthlyAggregates AS (
    SELECT 
        d.Year,
        d.Month,
        d.Year * 100 + d.Month AS YearMonthKey,
        MAX(d.MonthName) AS MonthName,
        SUM(f.SalesAmount) AS MonthlyRevenue,
        SUM(f.ProfitAmount) AS MonthlyProfit,
        COUNT(DISTINCT f.OrderID) AS MonthlyOrders
    FROM dw.FactSales f
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY d.Year, d.Month, d.Year * 100 + d.Month
)
SELECT 
    Year,
    Month,
    MonthName,
    MonthlyRevenue,
    MonthlyProfit,
    MonthlyOrders,
    LAG(MonthlyRevenue, 1) OVER (ORDER BY YearMonthKey) AS PrevMonthRevenue,
    ROUND(
        (MonthlyRevenue - LAG(MonthlyRevenue, 1) OVER (ORDER BY YearMonthKey)) 
        / NULLIF(LAG(MonthlyRevenue, 1) OVER (ORDER BY YearMonthKey), 0) * 100, 
        2
    ) AS MoM_Revenue_Growth_Percent,
    SUM(MonthlyRevenue) OVER (PARTITION BY Year ORDER BY Month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS YTD_Revenue
FROM MonthlyAggregates
ORDER BY YearMonthKey;
GO

-- 3. Year-over-Year (YoY) Performance Comparison
WITH YearlySales AS (
    SELECT 
        d.Year,
        SUM(f.SalesAmount) AS AnnualRevenue,
        SUM(f.ProfitAmount) AS AnnualProfit,
        COUNT(DISTINCT f.OrderID) AS AnnualOrders,
        SUM(f.Quantity) AS AnnualUnits
    FROM dw.FactSales f
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY d.Year
)
SELECT 
    Year,
    AnnualRevenue,
    AnnualProfit,
    AnnualOrders,
    AnnualUnits,
    LAG(AnnualRevenue, 1) OVER (ORDER BY Year) AS PriorYearRevenue,
    ROUND(
        (AnnualRevenue - LAG(AnnualRevenue, 1) OVER (ORDER BY Year)) 
        / NULLIF(LAG(AnnualRevenue, 1) OVER (ORDER BY Year), 0) * 100, 
        2
    ) AS YoY_Revenue_Growth_Percent,
    ROUND(AnnualProfit / NULLIF(AnnualRevenue, 0) * 100, 2) AS AnnualMarginPercent
FROM YearlySales
ORDER BY Year;
GO

-- 4. Category Revenue Contribution & Margin Analysis
SELECT 
    dp.CategoryID,
    dp.CategoryName,
    SUM(f.Quantity) AS UnitsSold,
    SUM(f.SalesAmount) AS TotalRevenue,
    ROUND(SUM(f.SalesAmount) / SUM(SUM(f.SalesAmount)) OVER() * 100, 2) AS RevenueContributionPercent,
    SUM(f.ProfitAmount) AS TotalProfit,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS GrossMarginPercent,
    RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS RevenueRank
FROM dw.FactSales f
INNER JOIN dw.DimProduct dp ON f.ProductKey = dp.ProductKey
GROUP BY dp.CategoryID, dp.CategoryName
ORDER BY TotalRevenue DESC;
GO

-- 5. Impact of Promotional Discounts on Profit Margins
SELECT 
    CASE 
        WHEN DiscountAmount = 0 THEN 'Full Price (No Discount)'
        WHEN DiscountAmount / NULLIF(SalesAmount + DiscountAmount, 0) <= 0.10 THEN 'Low Discount (<= 10%)'
        WHEN DiscountAmount / NULLIF(SalesAmount + DiscountAmount, 0) <= 0.20 THEN 'Medium Discount (11-20%)'
        ELSE 'Deep Discount (> 20%)'
    END AS DiscountTier,
    COUNT(SalesKey) AS TransactionCount,
    SUM(SalesAmount) AS TotalSales,
    SUM(DiscountAmount) AS TotalDiscountGiven,
    SUM(ProfitAmount) AS TotalProfit,
    ROUND(SUM(ProfitAmount) / NULLIF(SUM(SalesAmount), 0) * 100, 2) AS EffectiveProfitMarginPercent
FROM dw.FactSales
GROUP BY 
    CASE 
        WHEN DiscountAmount = 0 THEN 'Full Price (No Discount)'
        WHEN DiscountAmount / NULLIF(SalesAmount + DiscountAmount, 0) <= 0.10 THEN 'Low Discount (<= 10%)'
        WHEN DiscountAmount / NULLIF(SalesAmount + DiscountAmount, 0) <= 0.20 THEN 'Medium Discount (11-20%)'
        ELSE 'Deep Discount (> 20%)'
    END
ORDER BY TotalSales DESC;
GO
