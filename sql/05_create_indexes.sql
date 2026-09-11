-- ============================================================================
-- SCRIPT: 05_create_indexes.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates B-Tree nonclustered indexes on foreign keys and a Nonclustered
--              Columnstore Index (NCCI) on FactSales for sub-second analytical reporting.
-- ============================================================================

USE VeyraDW;
GO

-- 1. FactSales B-Tree Indexes on Foreign Keys
CREATE NONCLUSTERED INDEX IX_FactSales_CustomerKey ON dw.FactSales (CustomerKey) INCLUDE (SalesAmount, ProfitAmount);
CREATE NONCLUSTERED INDEX IX_FactSales_ProductKey ON dw.FactSales (ProductKey) INCLUDE (Quantity, SalesAmount, ProfitAmount);
CREATE NONCLUSTERED INDEX IX_FactSales_OrderDateKey ON dw.FactSales (OrderDateKey) INCLUDE (SalesAmount, ProfitAmount);
CREATE NONCLUSTERED INDEX IX_FactSales_LocationKey ON dw.FactSales (LocationKey);
CREATE NONCLUSTERED INDEX IX_FactSales_PaymentKey ON dw.FactSales (PaymentKey);
CREATE NONCLUSTERED INDEX IX_FactSales_OrderID ON dw.FactSales (OrderID);
GO

-- 2. Nonclustered Columnstore Index on FactSales for high-performance aggregations over 2M+ rows
CREATE NONCLUSTERED COLUMNSTORE INDEX NCCIX_FactSales ON dw.FactSales (
    OrderDateKey,
    CustomerKey,
    ProductKey,
    LocationKey,
    PaymentKey,
    Quantity,
    UnitPrice,
    DiscountAmount,
    SalesAmount,
    CostAmount,
    ProfitAmount,
    OrderStatus
);
GO

-- 3. FactReturns Indexes
CREATE NONCLUSTERED INDEX IX_FactReturns_CustomerKey ON dw.FactReturns (CustomerKey);
CREATE NONCLUSTERED INDEX IX_FactReturns_ProductKey ON dw.FactReturns (ProductKey);
CREATE NONCLUSTERED INDEX IX_FactReturns_ReturnDateKey ON dw.FactReturns (ReturnDateKey);
CREATE NONCLUSTERED INDEX IX_FactReturns_OrderID ON dw.FactReturns (OrderID);
GO

-- 4. Dimension Business Key Indexes
CREATE UNIQUE NONCLUSTERED INDEX IX_DimCustomer_CustomerID ON dw.DimCustomer (CustomerID);
CREATE UNIQUE NONCLUSTERED INDEX IX_DimProduct_ProductID ON dw.DimProduct (ProductID);
CREATE NONCLUSTERED INDEX IX_DimProduct_CategoryID ON dw.DimProduct (CategoryID);
CREATE NONCLUSTERED INDEX IX_DimLocation_Combo ON dw.DimLocation (Country, Region, State, City);
GO

PRINT 'Indexes and Columnstore index created successfully.';
GO
