-- ============================================================================
-- SCRIPT: 13_clv_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Customer Lifetime Value (CLV) calculation and value tiering
--              using documented mathematical formulas in T-SQL.
-- ============================================================================

USE VeyraDW;
GO

WITH CustomerHistorical AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.AcquisitionChannel,
        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.SalesAmount) AS TotalRevenue,
        SUM(f.ProfitAmount) AS TotalProfit,
        MIN(d.FullDate) AS FirstOrderDate,
        MAX(d.FullDate) AS LastOrderDate
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.AcquisitionChannel
),
CLV_Calculated AS (
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
        -- Annualized purchase frequency over 4-year observation window (2022-2025)
        ROUND(CAST(TotalOrders AS FLOAT) / 4.0, 2) AS AnnualPurchaseFrequency,
        -- Projected Future Margin: Annualized Orders * AOV * MarginRate * 2.125 Future Multiplier
        ROUND(
            (CAST(TotalOrders AS FLOAT) / 4.0) * 
            (TotalRevenue / NULLIF(TotalOrders, 0)) * 
            (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125, 
            2
        ) AS EstimatedFutureValue,
        -- Total Estimated CLV = Historical Profit + Projected Future Margin
        ROUND(
            TotalProfit + 
            ((CAST(TotalOrders AS FLOAT) / 4.0) * 
            (TotalRevenue / NULLIF(TotalOrders, 0)) * 
            (TotalProfit / NULLIF(TotalRevenue, 0)) * 2.125),
            2
        ) AS EstimatedCLV
    FROM CustomerHistorical
)
SELECT 
    CASE 
        WHEN EstimatedCLV >= 2500 THEN 'Platinum VIP ($2,500+)'
        WHEN EstimatedCLV >= 1000 THEN 'Gold ($1,000 - $2,499)'
        WHEN EstimatedCLV >= 400  THEN 'Silver ($400 - $999)'
        ELSE 'Bronze (< $400)'
    END AS CLV_Tier,
    COUNT(CustomerID) AS CustomerCount,
    ROUND(COUNT(CustomerID) * 100.0 / SUM(COUNT(CustomerID)) OVER (), 2) AS CustomerSharePercent,
    ROUND(SUM(TotalRevenue), 2) AS HistoricalRevenue,
    ROUND(SUM(TotalProfit), 2) AS HistoricalProfit,
    ROUND(SUM(EstimatedCLV), 2) AS ProjectedPortfolioCLV,
    ROUND(AVG(EstimatedCLV), 2) AS AvgCLVPerCustomer
FROM CLV_Calculated
GROUP BY 
    CASE 
        WHEN EstimatedCLV >= 2500 THEN 'Platinum VIP ($2,500+)'
        WHEN EstimatedCLV >= 1000 THEN 'Gold ($1,000 - $2,499)'
        WHEN EstimatedCLV >= 400  THEN 'Silver ($400 - $999)'
        ELSE 'Bronze (< $400)'
    END
ORDER BY ProjectedPortfolioCLV DESC;
GO
