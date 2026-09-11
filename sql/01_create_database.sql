-- ============================================================================
-- SCRIPT: 01_create_database.sql
-- PROJECT: Veyra E-Commerce Sales Analytics & Customer Segmentation
-- DESCRIPTION: Creates the production Data Warehouse database VeyraDW.
-- TARGET: Microsoft SQL Server 2017+
-- ============================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'VeyraDW')
BEGIN
    CREATE DATABASE VeyraDW
    COLLATE Latin1_General_100_CI_AS_SC_UTF8;
    PRINT 'Database VeyraDW created successfully.';
END
ELSE
BEGIN
    PRINT 'Database VeyraDW already exists.';
END
GO

ALTER DATABASE VeyraDW SET RECOVERY SIMPLE;
ALTER DATABASE VeyraDW SET AUTO_UPDATE_STATISTICS ON;
ALTER DATABASE VeyraDW SET ALLOW_SNAPSHOT_ISOLATION ON;
GO

USE VeyraDW;
GO
