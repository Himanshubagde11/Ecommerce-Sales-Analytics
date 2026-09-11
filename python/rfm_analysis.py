"""
RFM (Recency, Frequency, Monetary) Customer Segmentation for Veyra E-Commerce.
Calculates documented 1-5 quintile scores and business segments from actual purchase behavior.
Exports reports/rfm_customer_segments.csv.
"""

import pandas as pd
import numpy as np
from config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    setup_logger
)

logger = setup_logger("rfm_analysis")

def run_rfm_analysis() -> pd.DataFrame:
    """Executes customer-level RFM scoring and segmentation."""
    logger.info("Starting RFM Customer Segmentation Analysis...")

    # Load cleaned sales and customers
    sales = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv", usecols=["OrderID", "CustomerID", "OrderDate", "SalesAmount"])
    customers = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv", usecols=["CustomerID", "CustomerName", "Email", "Country", "Region"])

    sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
    ref_date = sales["OrderDate"].max() + pd.Timedelta(days=1)
    logger.info(f"RFM Reference Analysis Date: {ref_date.strftime('%Y-%m-%d')}")

    # Aggregate by customer
    rfm = sales.groupby("CustomerID").agg(
        LastOrderDate=("OrderDate", "max"),
        Frequency=("OrderID", "nunique"),
        Monetary=("SalesAmount", "sum")
    ).reset_index()

    rfm["Recency"] = (ref_date - rfm["LastOrderDate"]).dt.days
    rfm["Monetary"] = rfm["Monetary"].round(2)

    # Merge all customers to account for customers with 0 orders (if any)
    rfm = customers.merge(rfm, on="CustomerID", how="left")
    rfm["Frequency"] = rfm["Frequency"].fillna(0).astype(int)
    rfm["Monetary"] = rfm["Monetary"].fillna(0.0)
    rfm["Recency"] = rfm["Recency"].fillna(999).astype(int)

    # Compute 1-5 Scores using robust percentile rank method
    # Recency: Lower recency is better (higher score)
    rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Frequency: Higher frequency is better
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first", ascending=True), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Monetary: Higher spend is better
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first", ascending=True), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    # Segment Mapping Function based on actual RFM behavior
    def assign_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        if r <= 2 and f >= 4 and m >= 4:
            return "Cannot Lose Them"
        if r <= 2 and f >= 3:
            return "At Risk"
        if r >= 4 and f in [2, 3]:
            return "Potential Loyalists"
        if r >= 4 and f == 1:
            return "New Customers"
        if r == 3 and f == 1:
            return "Promising"
        if r in [2, 3] and f in [2, 3]:
            return "Need Attention"
        if r <= 2 and f <= 2:
            return "Lost Customers"
        return "Need Attention"

    rfm["RFM_Segment"] = rfm.apply(assign_segment, axis=1)

    # Segment Summary
    summary = rfm["RFM_Segment"].value_counts().reset_index()
    summary.columns = ["Segment", "CustomerCount"]
    summary["Percentage"] = (summary["CustomerCount"] / len(rfm) * 100).round(2)
    logger.info("RFM Segmentation Distribution:\n" + summary.to_string(index=False))

    out_file = REPORTS_DIR / "rfm_customer_segments.csv"
    cols_to_export = [
        "CustomerID", "CustomerName", "Email", "Country", "Region",
        "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score",
        "RFM_Score", "RFM_Segment"
    ]
    rfm[cols_to_export].to_csv(out_file, index=False)
    logger.info(f"RFM analysis exported successfully -> {out_file}")
    return rfm

if __name__ == "__main__":
    run_rfm_analysis()
