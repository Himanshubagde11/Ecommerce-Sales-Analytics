-- ============================================================================
-- SCRIPT: 03_create_dimensions.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates Dimension tables for the Star Schema with surrogate keys,
--              constraints, and date dimension population logic.
-- ============================================================================

USE VeyraDW;
GO

-- 1. DimCategory
IF OBJECT_ID('dw.DimCategory', 'U') IS NOT NULL DROP TABLE dw.DimCategory;
CREATE TABLE dw.DimCategory (
    CategoryID INT NOT NULL CONSTRAINT PK_DimCategory PRIMARY KEY CLUSTERED,
    CategoryName VARCHAR(50) NOT NULL,
    Description VARCHAR(250) NULL
);
GO

-- 2. DimProduct
IF OBJECT_ID('dw.DimProduct', 'U') IS NOT NULL DROP TABLE dw.DimProduct;
CREATE TABLE dw.DimProduct (
    ProductKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimProduct PRIMARY KEY CLUSTERED,
    ProductID INT NOT NULL,
    ProductName VARCHAR(200) NOT NULL,
    Brand VARCHAR(100) NOT NULL,
    CategoryID INT NOT NULL CONSTRAINT FK_DimProduct_Category REFERENCES dw.DimCategory(CategoryID),
    CategoryName VARCHAR(50) NOT NULL,
    UnitCost DECIMAL(18,2) NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    ProductLaunchDate DATE NOT NULL,
    CreatedDate DATETIME2 NOT NULL CONSTRAINT DF_DimProduct_Created DEFAULT SYSUTCDATETIME()
);
GO

-- 3. DimLocation
IF OBJECT_ID('dw.DimLocation', 'U') IS NOT NULL DROP TABLE dw.DimLocation;
CREATE TABLE dw.DimLocation (
    LocationKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimLocation PRIMARY KEY CLUSTERED,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Region VARCHAR(50) NOT NULL
);
GO

-- 4. DimCustomer
IF OBJECT_ID('dw.DimCustomer', 'U') IS NOT NULL DROP TABLE dw.DimCustomer;
CREATE TABLE dw.DimCustomer (
    CustomerKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimCustomer PRIMARY KEY CLUSTERED,
    CustomerID INT NOT NULL,
    CustomerName VARCHAR(150) NOT NULL,
    Gender VARCHAR(20) NOT NULL,
    Age INT NOT NULL,
    SignupDate DATE NOT NULL,
    Email VARCHAR(150) NOT NULL,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Region VARCHAR(50) NOT NULL,
    AcquisitionChannel VARCHAR(50) NOT NULL,
    CreatedDate DATETIME2 NOT NULL CONSTRAINT DF_DimCustomer_Created DEFAULT SYSUTCDATETIME()
);
GO

-- 5. DimPayment
IF OBJECT_ID('dw.DimPayment', 'U') IS NOT NULL DROP TABLE dw.DimPayment;
CREATE TABLE dw.DimPayment (
    PaymentKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimPayment PRIMARY KEY CLUSTERED,
    PaymentMethod VARCHAR(50) NOT NULL CONSTRAINT UQ_DimPayment_Method UNIQUE
);
GO

-- 6. DimDate (Calendar Table: 2021-01-01 to 2026-12-31)
IF OBJECT_ID('dw.DimDate', 'U') IS NOT NULL DROP TABLE dw.DimDate;
CREATE TABLE dw.DimDate (
    DateKey INT NOT NULL CONSTRAINT PK_DimDate PRIMARY KEY CLUSTERED, -- e.g., 20231124
    FullDate DATE NOT NULL,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    QuarterName VARCHAR(10) NOT NULL,
    Month INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayOfMonth INT NOT NULL,
    DayOfWeek INT NOT NULL,
    DayName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL,
    IsHolidaySeason BIT NOT NULL,
    FiscalYear INT NOT NULL,
    FiscalQuarter VARCHAR(10) NOT NULL
);
GO

-- Populate DimDate
SET NOCOUNT ON;
DECLARE @StartDate DATE = '2021-01-01';
DECLARE @EndDate DATE = '2026-12-31';

WITH DateSequence AS (
    SELECT @StartDate AS CurrentDate
    UNION ALL
    SELECT DATEADD(DAY, 1, CurrentDate)
    FROM DateSequence
    WHERE CurrentDate < @EndDate
)
INSERT INTO dw.DimDate (
    DateKey, FullDate, Year, Quarter, QuarterName, Month, MonthName,
    DayOfMonth, DayOfWeek, DayName, IsWeekend, IsHolidaySeason,
    FiscalYear, FiscalQuarter
)
SELECT 
    CAST(CONVERT(VARCHAR(8), CurrentDate, 112) AS INT) AS DateKey,
    CurrentDate AS FullDate,
    DATEPART(YEAR, CurrentDate) AS Year,
    DATEPART(QUARTER, CurrentDate) AS Quarter,
    'Q' + CAST(DATEPART(QUARTER, CurrentDate) AS VARCHAR(1)) AS QuarterName,
    DATEPART(MONTH, CurrentDate) AS Month,
    DATENAME(MONTH, CurrentDate) AS MonthName,
    DATEPART(DAY, CurrentDate) AS DayOfMonth,
    DATEPART(WEEKDAY, CurrentDate) AS DayOfWeek,
    DATENAME(WEEKDAY, CurrentDate) AS DayName,
    CASE WHEN DATEPART(WEEKDAY, CurrentDate) IN (1, 7) THEN 1 ELSE 0 END AS IsWeekend,
    CASE WHEN DATEPART(MONTH, CurrentDate) IN (11, 12) THEN 1 ELSE 0 END AS IsHolidaySeason,
    DATEPART(YEAR, CurrentDate) AS FiscalYear,
    'FQ' + CAST(DATEPART(QUARTER, CurrentDate) AS VARCHAR(1)) AS FiscalQuarter
FROM DateSequence
OPTION (MAXRECURSION 3000);
GO

PRINT 'Dimension tables created and DimDate populated successfully.';
GO
