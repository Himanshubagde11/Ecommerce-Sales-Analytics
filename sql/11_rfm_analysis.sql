-- ============================================================================
-- SCRIPT: 11_rfm_analysis.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Implements standard 1-5 RFM scoring and customer segmentation
--              purely in T-SQL using CTEs, NTILE(5), and CASE expressions.
-- ============================================================================

USE VeyraDW;
GO

-- Calculate RFM Metrics, Assign 1-5 Scores with NTILE, and Segment
WITH MaxReference AS (
    SELECT DATEADD(DAY, 1, MAX(d.FullDate)) AS RefDate
    FROM dw.FactSales f
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
),
CustomerRFM_Raw AS (
    SELECT 
        dc.CustomerKey,
        dc.CustomerID,
        dc.CustomerName,
        dc.Email,
        dc.Country,
        dc.Region,
        DATEDIFF(DAY, MAX(d.FullDate), (SELECT RefDate FROM MaxReference)) AS Recency,
        COUNT(DISTINCT f.OrderID) AS Frequency,
        SUM(f.SalesAmount) AS Monetary
    FROM dw.DimCustomer dc
    INNER JOIN dw.FactSales f ON dc.CustomerKey = f.CustomerKey
    INNER JOIN dw.DimDate d ON f.OrderDateKey = d.DateKey
    GROUP BY dc.CustomerKey, dc.CustomerID, dc.CustomerName, dc.Email, dc.Country, dc.Region
),
CustomerRFM_Scores AS (
    SELECT 
        CustomerKey,
        CustomerID,
        CustomerName,
        Country,
        Region,
        Recency,
        Frequency,
        Monetary,
        -- Recency: Lower value is better -> NTILE ordered descending gives 5 to most recent
        NTILE(5) OVER (ORDER BY Recency DESC) AS R_Score,
        -- Frequency: Higher value is better -> NTILE ordered ascending gives 5 to most frequent
        NTILE(5) OVER (ORDER BY Frequency ASC) AS F_Score,
        -- Monetary: Higher spend is better -> NTILE ordered ascending gives 5 to highest spenders
        NTILE(5) OVER (ORDER BY Monetary ASC) AS M_Score
    FROM CustomerRFM_Raw
),
CustomerRFM_Segments AS (
    SELECT 
        *,
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
    FROM CustomerRFM_Scores
)
-- Aggregated RFM Segment Distribution
SELECT 
    RFM_Segment,
    COUNT(CustomerKey) AS CustomerCount,
    ROUND(COUNT(CustomerKey) * 100.0 / SUM(COUNT(CustomerKey)) OVER (), 2) AS CustomerSharePercent,
    ROUND(SUM(Monetary), 2) AS SegmentTotalRevenue,
    ROUND(SUM(Monetary) * 100.0 / SUM(SUM(Monetary)) OVER (), 2) AS RevenueSharePercent,
    ROUND(AVG(Monetary), 2) AS AvgCustomerSpend,
    ROUND(AVG(CAST(Frequency AS FLOAT)), 2) AS AvgOrderFrequency,
    ROUND(AVG(CAST(Recency AS FLOAT)), 1) AS AvgRecencyDays
FROM CustomerRFM_Segments
GROUP BY RFM_Segment
ORDER BY SegmentTotalRevenue DESC;
GO
