"""
Explainable Churn Risk Framework for Veyra E-Commerce.
Evaluates customer purchase cadence, historical inter-purchase intervals,
and classifies customers into Low, Medium, and High Churn Risk cohorts.
Calculates Revenue at Risk without fabricating black-box ML claims.
Exports reports/churn_analysis.csv.
"""

import pandas as pd
import numpy as np
from config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    setup_logger
)

logger = setup_logger("churn_analysis")

def run_churn_analysis() -> pd.DataFrame:
    """Executes explainable rule-based churn risk calculation based on purchase intervals."""
    logger.info("Starting Explainable Customer Churn Risk Analysis...")

    # Load sales and customers
    sales = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv", usecols=["OrderID", "CustomerID", "OrderDate", "SalesAmount"])
    customers = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv", usecols=["CustomerID", "CustomerName", "Email", "Country", "Region"])

    sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
    ref_date = sales["OrderDate"].max() + pd.Timedelta(days=1)

    # Calculate customer transaction intervals
    agg = sales.groupby("CustomerID").agg(
        TotalRevenue=("SalesAmount", "sum"),
        TotalOrders=("OrderID", "nunique"),
        FirstOrderDate=("OrderDate", "min"),
        LastOrderDate=("OrderDate", "max")
    ).reset_index()

    agg["DaysSinceLastPurchase"] = (ref_date - agg["LastOrderDate"]).dt.days
    agg["CustomerLifespanDays"] = (agg["LastOrderDate"] - agg["FirstOrderDate"]).dt.days
    agg["TotalRevenue"] = agg["TotalRevenue"].round(2)

    # Compute expected inter-purchase cycle for repeat customers
    # For repeat customers (Orders > 1): Average cadence = Lifespan / (Orders - 1)
    repeat_mask = agg["TotalOrders"] > 1
    agg["AvgInterPurchaseDays"] = np.nan
    agg.loc[repeat_mask, "AvgInterPurchaseDays"] = (
        agg.loc[repeat_mask, "CustomerLifespanDays"] / (agg.loc[repeat_mask, "TotalOrders"] - 1)
    ).clip(lower=7)

    # Assign explainable churn risk
    def evaluate_risk(row):
        days_since = row["DaysSinceLastPurchase"]
        orders = row["TotalOrders"]
        avg_cycle = row["AvgInterPurchaseDays"]

        if orders == 1:
            # Single-order customers: evaluate against calendar thresholds
            if days_since <= 90:
                return "Low Risk"
            elif days_since <= 270:
                return "Medium Risk"
            else:
                return "High Risk"
        else:
            # Repeat customers: compare to personal purchase cadence
            cycle = avg_cycle if not np.isnan(avg_cycle) else 90.0
            if days_since <= 1.5 * cycle:
                return "Low Risk"
            elif days_since <= 3.0 * cycle and days_since <= 365:
                return "Medium Risk"
            else:
                return "High Risk"

    agg["ChurnRisk"] = agg.apply(evaluate_risk, axis=1)

    # Calculate Revenue at Risk (Monetary spend of High Risk customers)
    agg["RevenueAtRisk"] = np.where(agg["ChurnRisk"] == "High Risk", agg["TotalRevenue"], 0.0)

    # Merge demographics
    result = customers.merge(agg, on="CustomerID", how="inner")

    # Summary Report
    risk_summary = result.groupby("ChurnRisk").agg(
        CustomerCount=("CustomerID", "count"),
        TotalRevenue=("TotalRevenue", "sum"),
        RevenueAtRisk=("RevenueAtRisk", "sum"),
        AvgDaysSinceLastOrder=("DaysSinceLastPurchase", "mean")
    ).reset_index()
    risk_summary["RevenuePercent"] = (risk_summary["TotalRevenue"] / risk_summary["TotalRevenue"].sum() * 100).round(2)
    risk_summary["CustomerPercent"] = (risk_summary["CustomerCount"] / len(result) * 100).round(2)

    logger.info("Churn Risk Distribution Summary:\n" + risk_summary.to_string(index=False))

    out_file = REPORTS_DIR / "churn_analysis.csv"
    export_cols = [
        "CustomerID", "CustomerName", "Country", "Region", "TotalOrders",
        "TotalRevenue", "DaysSinceLastPurchase", "CustomerLifespanDays",
        "AvgInterPurchaseDays", "ChurnRisk", "RevenueAtRisk"
    ]
    result[export_cols].to_csv(out_file, index=False)
    logger.info(f"Churn analysis exported successfully -> {out_file}")

    return result

if __name__ == "__main__":
    run_churn_analysis()
