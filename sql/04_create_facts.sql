-- ============================================================================
-- SCRIPT: 04_create_facts.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates FactSales and FactReturns tables with strict relational integrity,
--              surrogate foreign keys, check constraints, and default timestamps.
-- ============================================================================

USE VeyraDW;
GO

-- 1. FactSales (2M+ Grain Table: One row per order line item)
IF OBJECT_ID('dw.FactSales', 'U') IS NOT NULL DROP TABLE dw.FactSales;
CREATE TABLE dw.FactSales (
    SalesKey BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactSales PRIMARY KEY CLUSTERED,
    SalesID INT NOT NULL,
    OrderID INT NOT NULL,
    CustomerKey INT NOT NULL CONSTRAINT FK_FactSales_Customer REFERENCES dw.DimCustomer(CustomerKey),
    ProductKey INT NOT NULL CONSTRAINT FK_FactSales_Product REFERENCES dw.DimProduct(ProductKey),
    OrderDateKey INT NOT NULL CONSTRAINT FK_FactSales_OrderDate REFERENCES dw.DimDate(DateKey),
    LocationKey INT NOT NULL CONSTRAINT FK_FactSales_Location REFERENCES dw.DimLocation(LocationKey),
    PaymentKey INT NOT NULL CONSTRAINT FK_FactSales_Payment REFERENCES dw.DimPayment(PaymentKey),
    OrderStatus VARCHAR(30) NOT NULL,
    ShippingMethod VARCHAR(50) NOT NULL,
    Quantity INT NOT NULL CONSTRAINT CK_FactSales_Quantity CHECK (Quantity > 0),
    UnitPrice DECIMAL(18,2) NOT NULL CONSTRAINT CK_FactSales_UnitPrice CHECK (UnitPrice >= 0),
    DiscountAmount DECIMAL(18,2) NOT NULL CONSTRAINT CK_FactSales_Discount CHECK (DiscountAmount >= 0),
    SalesAmount DECIMAL(18,2) NOT NULL,
    CostAmount DECIMAL(18,2) NOT NULL CONSTRAINT CK_FactSales_Cost CHECK (CostAmount >= 0),
    ProfitAmount DECIMAL(18,2) NOT NULL,
    CreatedDate DATETIME2 NOT NULL CONSTRAINT DF_FactSales_Created DEFAULT SYSUTCDATETIME()
);
GO

-- 2. FactReturns (Grain: One row per returned item line)
IF OBJECT_ID('dw.FactReturns', 'U') IS NOT NULL DROP TABLE dw.FactReturns;
CREATE TABLE dw.FactReturns (
    ReturnKey BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactReturns PRIMARY KEY CLUSTERED,
    ReturnID INT NOT NULL,
    OrderID INT NOT NULL,
    CustomerKey INT NOT NULL CONSTRAINT FK_FactReturns_Customer REFERENCES dw.DimCustomer(CustomerKey),
    ProductKey INT NOT NULL CONSTRAINT FK_FactReturns_Product REFERENCES dw.DimProduct(ProductKey),
    ReturnDateKey INT NOT NULL CONSTRAINT FK_FactReturns_ReturnDate REFERENCES dw.DimDate(DateKey),
    QuantityReturned INT NOT NULL CONSTRAINT CK_FactReturns_Quantity CHECK (QuantityReturned > 0),
    ReturnAmount DECIMAL(18,2) NOT NULL CONSTRAINT CK_FactReturns_Amount CHECK (ReturnAmount > 0),
    ReturnReason VARCHAR(100) NOT NULL,
    CreatedDate DATETIME2 NOT NULL CONSTRAINT DF_FactReturns_Created DEFAULT SYSUTCDATETIME()
);
GO

PRINT 'Fact tables created successfully.';
GO
