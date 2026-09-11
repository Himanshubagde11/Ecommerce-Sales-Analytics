-- ============================================================================
-- SCRIPT: 12_churn_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Explainable behavioral churn risk framework and revenue-at-risk
--              quantification using T-SQL window functions and date mathematics.
-- ============================================================================

USE VeyraDW;
GO

WITH MaxReference AS (
    SELECT DATEADD(DAY, 1, MAX(d.FullDate)) AS RefDate
    FROM dw.FactSales f
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
),
CustomerCadence AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.Email,
        dc.Country,
        dc.Region,
        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.SalesAmount) AS TotalRevenue,
        MIN(d.FullDate) AS FirstOrderDate,
        MAX(d.FullDate) AS LastOrderDate,
        DATEDIFF(DAY, MAX(d.FullDate), (SELECT RefDate FROM MaxReference)) AS DaysSinceLastPurchase,
        DATEDIFF(DAY, MIN(d.FullDate), MAX(d.FullDate)) AS CustomerLifespanDays
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.Email, dc.Country, dc.Region
),
CustomerIntervals AS (
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
    FROM CustomerCadence
),
ChurnClassification AS (
    SELECT 
        *,
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
        END AS ChurnRisk
    FROM CustomerIntervals
)
-- Aggregate Churn Risk Summary with Revenue at Risk
SELECT 
    ChurnRisk,
    COUNT(CustomerID) AS CustomerCount,
    ROUND(COUNT(CustomerID) * 100.0 / SUM(COUNT(CustomerID)) OVER (), 2) AS CustomerSharePercent,
    ROUND(SUM(TotalRevenue), 2) AS CumulativeHistoricalRevenue,
    ROUND(SUM(CASE WHEN ChurnRisk = 'High Risk' THEN TotalRevenue ELSE 0 END), 2) AS RevenueAtRisk,
    ROUND(AVG(CAST(DaysSinceLastPurchase AS FLOAT)), 1) AS AvgDaysSinceLastPurchase,
    ROUND(AVG(CAST(TotalOrders AS FLOAT)), 2) AS AvgLifetimeOrders
FROM ChurnClassification
GROUP BY ChurnRisk
ORDER BY CumulativeHistoricalRevenue DESC;
GO
