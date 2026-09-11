-- ============================================================================
-- SCRIPT: 09_customer_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Customer Behavior, Retention, Pareto Concentration, and Acquisition
--              Channel Performance using Advanced Window Functions and CTEs.
-- ============================================================================

USE VeyraDW;
GO

-- 1. High-Level Customer Base Overview & Repeat Customer Rate
WITH CustomerOrderCounts AS (
    SELECT 
        dc.CustomerKey,
        COUNT(DISTINCT f.OrderID) AS OrderCount,
        SUM(f.SalesAmount) AS LifetimeSpend,
        SUM(f.ProfitAmount) AS LifetimeProfit
    FROM dw.DimCustomer dc
    LEFT JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    GROUP BY dc.CustomerKey
)
SELECT 
    COUNT(CustomerKey) AS TotalRegisteredCustomers,
    SUM(CASE WHEN OrderCount > 0 THEN 1 ELSE 0 END) AS PurchasingCustomers,
    SUM(CASE WHEN OrderCount = 1 THEN 1 ELSE 0 END) AS OneTimeBuyers,
    SUM(CASE WHEN OrderCount > 1 THEN 1 ELSE 0 END) AS RepeatCustomers,
    ROUND(CAST(SUM(CASE WHEN OrderCount > 1 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(SUM(CASE WHEN OrderCount > 0 THEN 1 ELSE 0 END), 0) * 100, 2) AS RepeatCustomerRatePercent,
    ROUND(AVG(CAST(OrderCount AS FLOAT)), 2) AS AvgOrdersPerCustomer,
    ROUND(AVG(LifetimeSpend), 2) AS AvgLifetimeSpendPerCustomer
FROM CustomerOrderCounts;
GO

-- 2. Pareto Revenue Concentration Analysis (Top 20% vs. Total Revenue)
WITH RankedCustomers AS (
    SELECT 
        dc.CustomerID,
        dc.CustomerName,
        SUM(f.SalesAmount) AS TotalRevenue,
        SUM(f.ProfitAmount) AS TotalProfit,
        ROW_NUMBER() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS CustomerRank,
        COUNT(*) OVER () AS TotalCustomerCount,
        SUM(SUM(f.SalesAmount)) OVER () AS EnterpriseTotalRevenue
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    GROUP BY dc.CustomerID, dc.CustomerName
),
CumulativeCalculation AS (
    SELECT 
        CustomerID,
        CustomerName,
        TotalRevenue,
        TotalProfit,
        CustomerRank,
        TotalCustomerCount,
        EnterpriseTotalRevenue,
        CAST(CustomerRank AS FLOAT) / TotalCustomerCount * 100 AS CustomerPercentile,
        SUM(TotalRevenue) OVER (ORDER BY CustomerRank ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CumulativeRevenue
    FROM RankedCustomers
)
SELECT 
    CASE 
        WHEN CustomerPercentile <= 10.0 THEN 'Top 10% Customers'
        WHEN CustomerPercentile <= 20.0 THEN 'Top 11-20% Customers'
        WHEN CustomerPercentile <= 50.0 THEN 'Top 21-50% Customers'
        ELSE 'Bottom 50% Customers'
    END AS CustomerCohort,
    COUNT(CustomerID) AS CohortCustomerCount,
    ROUND(SUM(TotalRevenue), 2) AS CohortTotalRevenue,
    ROUND(SUM(TotalRevenue) / MAX(EnterpriseTotalRevenue) * 100, 2) AS RevenueSharePercent,
    ROUND(SUM(TotalProfit), 2) AS CohortTotalProfit
FROM CumulativeCalculation
GROUP BY 
    CASE 
        WHEN CustomerPercentile <= 10.0 THEN 'Top 10% Customers'
        WHEN CustomerPercentile <= 20.0 THEN 'Top 11-20% Customers'
        WHEN CustomerPercentile <= 50.0 THEN 'Top 21-50% Customers'
        ELSE 'Bottom 50% Customers'
    END
ORDER BY CohortTotalRevenue DESC;
GO

-- 3. Top 20 Most Valuable Customers (Ranked by Revenue & Profit Contribution)
WITH CustomerTotals AS (
    SELECT 
        dc.CustomerID,
        dc.CustomerName,
        dc.Email,
        dc.Country,
        dc.Region,
        dc.AcquisitionChannel,
        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.Quantity) AS TotalUnitsBought,
        SUM(f.SalesAmount) AS TotalRevenue,
        SUM(f.ProfitAmount) AS TotalProfit,
        ROUND(SUM(f.SalesAmount) / NULLIF(COUNT(DISTINCT f.OrderID), 0), 2) AS AOV
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    GROUP BY dc.CustomerID, dc.CustomerName, dc.Email, dc.Country, dc.Region, dc.AcquisitionChannel
)
SELECT TOP 20
    CustomerID,
    CustomerName,
    Country,
    Region,
    AcquisitionChannel,
    TotalOrders,
    TotalUnitsBought,
    TotalRevenue,
    TotalProfit,
    AOV,
    DENSE_RANK() OVER (ORDER BY TotalRevenue DESC) AS RevenueRank,
    DENSE_RANK() OVER (ORDER BY TotalProfit DESC) AS ProfitRank
FROM CustomerTotals
ORDER BY TotalRevenue DESC;
GO

-- 4. Customer Acquisition Channel Performance Comparison
SELECT 
    dc.AcquisitionChannel,
    COUNT(DISTINCT dc.CustomerKey) AS AcquiredCustomers,
    COUNT(DISTINCT f.OrderID) AS TotalOrdersGenerated,
    SUM(f.SalesAmount) AS ChannelRevenue,
    SUM(f.ProfitAmount) AS ChannelProfit,
    ROUND(SUM(f.SalesAmount) / NULLIF(COUNT(DISTINCT dc.CustomerKey), 0), 2) AS AverageRevenuePerUser,
    ROUND(SUM(f.ProfitAmount) / NULLIF(SUM(f.SalesAmount), 0) * 100, 2) AS ChannelGrossMarginPercent,
    DENSE_RANK() OVER (ORDER BY SUM(f.SalesAmount) DESC) AS RevenueRank
FROM dw.DimCustomer dc
LEFT JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
GROUP BY dc.AcquisitionChannel
ORDER BY ChannelRevenue DESC;
GO
