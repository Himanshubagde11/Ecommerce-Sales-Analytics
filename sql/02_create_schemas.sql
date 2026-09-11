-- ============================================================================
-- SCRIPT: 02_create_schemas.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Establishes architectural schemas: stg (Staging), dw (Core Star Schema),
--              and analytics (Presentation Views for Power BI & BI Tools).
-- ============================================================================

USE VeyraDW;
GO

-- 1. Staging Schema (Raw Ingestion)
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'stg')
BEGIN
    EXEC('CREATE SCHEMA stg AUTHORIZATION dbo;');
    PRINT 'Schema [stg] created successfully.';
END
GO

-- 2. Data Warehouse Schema (Dimensional Model / Facts & Dimensions)
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'dw')
BEGIN
    EXEC('CREATE SCHEMA dw AUTHORIZATION dbo;');
    PRINT 'Schema [dw] created successfully.';
END
GO

-- 3. Analytics Schema (Power BI Analytical Views)
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'analytics')
BEGIN
    EXEC('CREATE SCHEMA analytics AUTHORIZATION dbo;');
    PRINT 'Schema [analytics] created successfully.';
END
GO
