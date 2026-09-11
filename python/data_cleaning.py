"""
ETL Data Cleaning Pipeline for Veyra E-Commerce.
Performs deduplication, missing value imputation, type casting,
bounds checking, and outputs processed production datasets and samples.
"""

import pandas as pd
import numpy as np
from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    setup_logger
)

logger = setup_logger("data_cleaning")

def clean_data():
    """Executes end-to-end data cleaning and generates processed and sample datasets."""
    logger.info("Starting Veyra Data Cleaning Pipeline...")

    # 1. Clean Customers
    logger.info("Cleaning Customers dataset...")
    cust_df = pd.read_csv(RAW_DATA_DIR / "customers.csv")
    initial_cust = len(cust_df)
    cust_df.drop_duplicates(subset=["CustomerID"], inplace=True)
    cust_df["Age"] = cust_df["Age"].clip(18, 100)
    cust_df["CustomerName"] = cust_df["CustomerName"].str.strip().str.title()
    cust_df["Email"] = cust_df["Email"].str.strip().str.lower()
    cust_df["City"] = cust_df["City"].str.strip()
    cust_df["State"] = cust_df["State"].str.strip()
    cust_df["Country"] = cust_df["Country"].str.strip()
    cust_df["Region"] = cust_df["Region"].str.strip()
    cust_df["SignupDate"] = pd.to_datetime(cust_df["SignupDate"]).dt.strftime('%Y-%m-%d')
    cust_df.to_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv", index=False)
    logger.info(f"Customers cleaned: {len(cust_df):,} records saved (initial: {initial_cust:,}).")

    # 2. Clean Products
    logger.info("Cleaning Products dataset...")
    prod_df = pd.read_csv(RAW_DATA_DIR / "products.csv")
    initial_prod = len(prod_df)
    prod_df.drop_duplicates(subset=["ProductID"], inplace=True)
    prod_df["ProductName"] = prod_df["ProductName"].str.strip()
    prod_df["Brand"] = prod_df["Brand"].str.strip()
    prod_df["CategoryName"] = prod_df["CategoryName"].str.strip()
    # Assert positive costs and prices
    prod_df["UnitCost"] = np.maximum(0.01, prod_df["UnitCost"].round(2))
    prod_df["UnitPrice"] = np.maximum(prod_df["UnitCost"] * 1.05, prod_df["UnitPrice"].round(2))
    prod_df["ProductLaunchDate"] = pd.to_datetime(prod_df["ProductLaunchDate"]).dt.strftime('%Y-%m-%d')
    prod_df.to_csv(PROCESSED_DATA_DIR / "cleaned_products.csv", index=False)
    logger.info(f"Products cleaned: {len(prod_df):,} records saved (initial: {initial_prod:,}).")

    # 3. Clean Orders
    logger.info("Cleaning Orders dataset...")
    orders_df = pd.read_csv(RAW_DATA_DIR / "orders.csv")
    initial_orders = len(orders_df)
    orders_df.drop_duplicates(subset=["OrderID"], inplace=True)
    orders_df["OrderDate"] = pd.to_datetime(orders_df["OrderDate"]).dt.strftime('%Y-%m-%d')
    orders_df["Discount"] = orders_df["Discount"].clip(0.0, 0.50).round(2)
    orders_df["TotalAmount"] = np.maximum(0.0, orders_df["TotalAmount"].round(2))
    orders_df.to_csv(PROCESSED_DATA_DIR / "cleaned_orders.csv", index=False)
    logger.info(f"Orders cleaned: {len(orders_df):,} records saved (initial: {initial_orders:,}).")

    # 4. Clean Sales (Order Lines)
    logger.info("Cleaning Sales transaction dataset...")
    sales_df = pd.read_csv(RAW_DATA_DIR / "sales.csv")
    initial_sales = len(sales_df)
    sales_df.drop_duplicates(subset=["SalesID"], inplace=True)
    sales_df["Quantity"] = sales_df["Quantity"].clip(1, 20).astype(int)
    sales_df["UnitPrice"] = np.maximum(0.01, sales_df["UnitPrice"].round(2))
    sales_df["DiscountAmount"] = np.maximum(0.0, sales_df["DiscountAmount"].round(2))
    
    # Enforce strict financial formulas
    sales_df["SalesAmount"] = np.round(sales_df["Quantity"] * sales_df["UnitPrice"] - sales_df["DiscountAmount"], 2)
    sales_df["CostAmount"] = np.round(sales_df["CostAmount"], 2)
    sales_df["ProfitAmount"] = np.round(sales_df["SalesAmount"] - sales_df["CostAmount"], 2)
    sales_df["OrderDate"] = pd.to_datetime(sales_df["OrderDate"]).dt.strftime('%Y-%m-%d')
    sales_df.to_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv", index=False)
    logger.info(f"Sales cleaned: {len(sales_df):,} records saved (initial: {initial_sales:,}).")

    # 5. Clean Returns
    logger.info("Cleaning Returns dataset...")
    returns_df = pd.read_csv(RAW_DATA_DIR / "returns.csv")
    initial_returns = len(returns_df)
    returns_df.drop_duplicates(subset=["ReturnID"], inplace=True)
    returns_df["QuantityReturned"] = np.maximum(1, returns_df["QuantityReturned"].astype(int))
    returns_df["ReturnAmount"] = np.maximum(0.01, returns_df["ReturnAmount"].round(2))
    returns_df["ReturnDate"] = pd.to_datetime(returns_df["ReturnDate"]).dt.strftime('%Y-%m-%d')
    returns_df["ReturnReason"] = returns_df["ReturnReason"].str.strip()
    returns_df.to_csv(PROCESSED_DATA_DIR / "cleaned_returns.csv", index=False)
    logger.info(f"Returns cleaned: {len(returns_df):,} records saved (initial: {initial_returns:,}).")

    # 6. Generate Representative Sample Datasets for Excel & Quick Audits
    logger.info("Generating representative sample datasets (5,000 orders)...")
    sample_orders = orders_df.sample(n=min(5000, len(orders_df)), random_state=42)
    sample_order_ids = set(sample_orders["OrderID"])
    sample_sales = sales_df[sales_df["OrderID"].isin(sample_order_ids)]
    sample_cust_ids = set(sample_orders["CustomerID"])
    sample_customers = cust_df[cust_df["CustomerID"].isin(sample_cust_ids)]

    sample_customers.to_csv(SAMPLE_DATA_DIR / "sample_customers.csv", index=False)
    sample_orders.to_csv(SAMPLE_DATA_DIR / "sample_orders.csv", index=False)
    sample_sales.to_csv(SAMPLE_DATA_DIR / "sample_sales.csv", index=False)
    logger.info("Sample datasets successfully created in data/sample/.")

    logger.info("Data cleaning completed successfully.")

if __name__ == "__main__":
    clean_data()
