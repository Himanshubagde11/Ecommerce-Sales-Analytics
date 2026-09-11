-- ============================================================================
-- SCRIPT: 06_load_staging.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates staging tables and provides high-speed BULK INSERT commands
--              to ingest CSV data into SQL Server.
-- ============================================================================

USE VeyraDW;
GO

-- 1. Create Staging Tables
IF OBJECT_ID('stg.Customers', 'U') IS NOT NULL DROP TABLE stg.Customers;
CREATE TABLE stg.Customers (
    CustomerID INT,
    CustomerName VARCHAR(150),
    Gender VARCHAR(20),
    Age INT,
    SignupDate VARCHAR(50),
    Email VARCHAR(150),
    City VARCHAR(100),
    State VARCHAR(100),
    Country VARCHAR(100),
    Region VARCHAR(50),
    AcquisitionChannel VARCHAR(50)
);

IF OBJECT_ID('stg.Products', 'U') IS NOT NULL DROP TABLE stg.Products;
CREATE TABLE stg.Products (
    ProductID INT,
    ProductName VARCHAR(200),
    Brand VARCHAR(100),
    CategoryID INT,
    CategoryName VARCHAR(50),
    UnitCost DECIMAL(18,2),
    UnitPrice DECIMAL(18,2),
    ProductLaunchDate VARCHAR(50)
);

IF OBJECT_ID('stg.Orders', 'U') IS NOT NULL DROP TABLE stg.Orders;
CREATE TABLE stg.Orders (
    OrderID INT,
    CustomerID INT,
    OrderDate VARCHAR(50),
    ShippingDate VARCHAR(50),
    DeliveryDate VARCHAR(50),
    OrderStatus VARCHAR(30),
    PaymentMethod VARCHAR(50),
    ShippingMethod VARCHAR(50),
    Discount DECIMAL(18,2),
    TotalAmount DECIMAL(18,2)
);

IF OBJECT_ID('stg.Sales', 'U') IS NOT NULL DROP TABLE stg.Sales;
CREATE TABLE stg.Sales (
    SalesID INT,
    OrderID INT,
    CustomerID INT,
    ProductID INT,
    OrderDate VARCHAR(50),
    Quantity INT,
    UnitPrice DECIMAL(18,2),
    DiscountAmount DECIMAL(18,2),
    SalesAmount DECIMAL(18,2),
    CostAmount DECIMAL(18,2),
    ProfitAmount DECIMAL(18,2)
);

IF OBJECT_ID('stg.Returns', 'U') IS NOT NULL DROP TABLE stg.Returns;
CREATE TABLE stg.Returns (
    ReturnID INT,
    OrderID INT,
    CustomerID INT,
    ProductID INT,
    ReturnDate VARCHAR(50),
    QuantityReturned INT,
    ReturnAmount DECIMAL(18,2),
    ReturnReason VARCHAR(100)
);
GO

-- ============================================================================
-- 2. BULK INSERT Procedures
-- Update the file paths below to match your environment before execution.
-- ============================================================================

TRUNCATE TABLE stg.Customers;
BULK INSERT stg.Customers
FROM 'D:\Portfolio Projects\E-commers sales analytics\data\processed\cleaned_customers.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    BATCHSIZE = 50000
);

TRUNCATE TABLE stg.Products;
BULK INSERT stg.Products
FROM 'D:\Portfolio Projects\E-commers sales analytics\data\processed\cleaned_products.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

TRUNCATE TABLE stg.Orders;
BULK INSERT stg.Orders
FROM 'D:\Portfolio Projects\E-commers sales analytics\data\processed\cleaned_orders.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    BATCHSIZE = 50000
);

TRUNCATE TABLE stg.Sales;
BULK INSERT stg.Sales
FROM 'D:\Portfolio Projects\E-commers sales analytics\data\processed\cleaned_sales.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    BATCHSIZE = 100000
);

TRUNCATE TABLE stg.Returns;
BULK INSERT stg.Returns
FROM 'D:\Portfolio Projects\E-commers sales analytics\data\processed\cleaned_returns.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    BATCHSIZE = 50000
);
GO
PRINT 'Staging tables and bulk insert scripts initialized.';
GO
