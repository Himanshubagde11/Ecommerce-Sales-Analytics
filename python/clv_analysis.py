"""
Customer Lifetime Value (CLV) Calculation Framework for Veyra E-Commerce.
Calculates historical customer value, annual purchase velocity, profit margin,
and projected Customer Lifetime Value using transparent, documented assumptions.
"""

import pandas as pd
import numpy as np
from config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    setup_logger
)

logger = setup_logger("clv_analysis")

def run_clv_analysis() -> pd.DataFrame:
    """Calculates customer-level CLV and financial contribution metrics."""
    logger.info("Starting Customer Lifetime Value (CLV) Modeling...")

    # Load cleaned datasets
    sales = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv", usecols=["OrderID", "CustomerID", "OrderDate", "SalesAmount", "ProfitAmount"])
    customers = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv", usecols=["CustomerID", "CustomerName", "Country", "Region", "AcquisitionChannel"])

    sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
    ref_date = sales["OrderDate"].max() + pd.Timedelta(days=1)

    # Aggregate customer sales performance
    cust_perf = sales.groupby("CustomerID").agg(
        TotalRevenue=("SalesAmount", "sum"),
        TotalProfit=("ProfitAmount", "sum"),
        TotalOrders=("OrderID", "nunique"),
        FirstOrderDate=("OrderDate", "min"),
        LastOrderDate=("OrderDate", "max")
    ).reset_index()

    cust_perf["CustomerLifespanDays"] = (cust_perf["LastOrderDate"] - cust_perf["FirstOrderDate"]).dt.days.clip(lower=1)
    cust_perf["AverageOrderValue"] = (cust_perf["TotalRevenue"] / cust_perf["TotalOrders"]).round(2)
    cust_perf["ProfitMarginRate"] = (cust_perf["TotalProfit"] / cust_perf["TotalRevenue"].clip(lower=1.0)).clip(0.05, 0.85).round(4)

    # Annualized Purchase Frequency (Orders per 365 days of observation)
    # Total observation window in years
    total_days_in_dataset = (ref_date - sales["OrderDate"].min()).days
    obs_years = max(1.0, total_days_in_dataset / 365.25)
    cust_perf["AnnualPurchaseFrequency"] = (cust_perf["TotalOrders"] / obs_years).round(2)

    # Documented CLV Estimation Model:
    # Assumptions:
    # 1. Expected future customer retention lifespan = 2.5 years
    # 2. Annual discount factor / retention decay = 0.85
    # 3. EstimatedCLV = TotalHistoricalProfit + (AnnualPurchaseFrequency * AverageOrderValue * ProfitMarginRate * FutureMultiplier)
    future_multiplier = 2.125 # 2.5 years * 0.85 discount
    
    annual_expected_profit = cust_perf["AnnualPurchaseFrequency"] * cust_perf["AverageOrderValue"] * cust_perf["ProfitMarginRate"]
    cust_perf["EstimatedFutureValue"] = (annual_expected_profit * future_multiplier).round(2)
    cust_perf["EstimatedCLV"] = (cust_perf["TotalProfit"] + cust_perf["EstimatedFutureValue"]).round(2)

    # Merge demographics
    clv_df = customers.merge(cust_perf, on="CustomerID", how="inner")

    logger.info(f"Calculated CLV metrics across {len(clv_df):,} customers.")
    logger.info(f"Average Total Revenue per Customer: ${clv_df['TotalRevenue'].mean():,.2f}")
    logger.info(f"Average Estimated CLV: ${clv_df['EstimatedCLV'].mean():,.2f}")
    logger.info(f"Median Estimated CLV: ${clv_df['EstimatedCLV'].median():,.2f}")

    return clv_df

if __name__ == "__main__":
    run_clv_analysis()
