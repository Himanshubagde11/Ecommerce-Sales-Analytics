-- ============================================================================
-- SCRIPT: 07_transform_to_dw.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: ELT transformation logic loading staging tables into the Star Schema
--              with surrogate key lookups and referential integrity resolution.
-- ============================================================================

USE VeyraDW;
GO

SET NOCOUNT ON;

PRINT 'Starting ELT Transformation: Staging -> Data Warehouse...';

-- 1. Populate DimCategory
INSERT INTO dw.DimCategory (CategoryID, CategoryName, Description)
SELECT DISTINCT 
    CategoryID,
    CategoryName,
    'Product category hierarchy for ' + CategoryName
FROM stg.Products
WHERE CategoryID NOT IN (SELECT CategoryID FROM dw.DimCategory);

-- 2. Populate DimLocation
INSERT INTO dw.DimLocation (City, State, Country, Region)
SELECT DISTINCT 
    City, State, Country, Region
FROM stg.Customers
EXCEPT
SELECT City, State, Country, Region
FROM dw.DimLocation;

-- 3. Populate DimPayment
INSERT INTO dw.DimPayment (PaymentMethod)
SELECT DISTINCT PaymentMethod
FROM stg.Orders
WHERE PaymentMethod NOT IN (SELECT PaymentMethod FROM dw.DimPayment);

-- 4. Populate DimCustomer
INSERT INTO dw.DimCustomer (
    CustomerID, CustomerName, Gender, Age, SignupDate,
    Email, City, State, Country, Region, AcquisitionChannel
)
SELECT 
    s.CustomerID,
    s.CustomerName,
    s.Gender,
    s.Age,
    CAST(s.SignupDate AS DATE),
    s.Email,
    s.City,
    s.State,
    s.Country,
    s.Region,
    s.AcquisitionChannel
FROM stg.Customers s
WHERE NOT EXISTS (
    SELECT 1 FROM dw.DimCustomer d WHERE d.CustomerID = s.CustomerID
);

-- 5. Populate DimProduct
INSERT INTO dw.DimProduct (
    ProductID, ProductName, Brand, CategoryID, CategoryName,
    UnitCost, UnitPrice, ProductLaunchDate
)
SELECT 
    s.ProductID,
    s.ProductName,
    s.Brand,
    s.CategoryID,
    s.CategoryName,
    s.UnitCost,
    s.UnitPrice,
    CAST(s.ProductLaunchDate AS DATE)
FROM stg.Products s
WHERE NOT EXISTS (
    SELECT 1 FROM dw.DimProduct d WHERE d.ProductID = s.ProductID
);

-- 6. Populate FactSales (2M+ grain)
PRINT 'Transforming and populating FactSales...';
INSERT INTO dw.FactSales (
    SalesID, OrderID, CustomerKey, ProductKey, OrderDateKey,
    LocationKey, PaymentKey, OrderStatus, ShippingMethod,
    Quantity, UnitPrice, DiscountAmount, SalesAmount, CostAmount, ProfitAmount
)
SELECT 
    s.SalesID,
    s.OrderID,
    dc.CustomerKey,
    dp.ProductKey,
    CAST(CONVERT(VARCHAR(8), CAST(s.OrderDate AS DATE), 112) AS INT) AS OrderDateKey,
    dl.LocationKey,
    dpm.PaymentKey,
    o.OrderStatus,
    o.ShippingMethod,
    s.Quantity,
    s.UnitPrice,
    s.DiscountAmount,
    s.SalesAmount,
    s.CostAmount,
    s.ProfitAmount
FROM stg.Sales s
INNER JOIN stg.Orders o ON s.OrderID = o.OrderID
INNER JOIN dw.DimCustomer dc ON s.CustomerID = dc.CustomerID
INNER JOIN dw.DimProduct dp ON s.ProductID = dp.ProductID
INNER JOIN dw.DimLocation dl ON dc.City = dl.City AND dc.State = dl.State AND dc.Country = dl.Country
INNER JOIN dw.DimPayment dpm ON o.PaymentMethod = dpm.PaymentMethod;

-- 7. Populate FactReturns
PRINT 'Transforming and populating FactReturns...';
INSERT INTO dw.FactReturns (
    ReturnID, OrderID, CustomerKey, ProductKey, ReturnDateKey,
    QuantityReturned, ReturnAmount, ReturnReason
)
SELECT 
    r.ReturnID,
    r.OrderID,
    dc.CustomerKey,
    dp.ProductKey,
    CAST(CONVERT(VARCHAR(8), CAST(r.ReturnDate AS DATE), 112) AS INT) AS ReturnDateKey,
    r.QuantityReturned,
    r.ReturnAmount,
    r.ReturnReason
FROM stg.Returns r
INNER JOIN dw.DimCustomer dc ON r.CustomerID = dc.CustomerID
INNER JOIN dw.DimProduct dp ON r.ProductID = dp.ProductID;

PRINT 'ELT Transformation completed successfully.';
GO
