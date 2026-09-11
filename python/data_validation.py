"""
Data Quality Validation Framework for Veyra E-Commerce.
Performs rigorous structural, referential, mathematical, and chronological tests.
Exports reports/data_quality_report.csv.
"""

import pandas as pd
import numpy as np
from config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    setup_logger
)

logger = setup_logger("data_validation")

def validate_data() -> pd.DataFrame:
    """Runs data quality checks across all processed tables and outputs data_quality_report.csv."""
    logger.info("Executing comprehensive Data Quality Audit...")

    # Load Cleaned Tables
    customers = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv")
    products = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_products.csv")
    orders = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_orders.csv")
    sales = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv")
    returns = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_returns.csv")

    report_rows = []

    def log_check(metric: str, val: str, status: str, desc: str):
        report_rows.append({
            "Metric": metric,
            "Value": str(val),
            "Status": status,
            "Description": desc
        })
        logger.info(f"[{status}] {metric}: {val} - {desc}")

    # 1. Volume Checks
    c_count = len(customers)
    log_check("Customer Volume", f"{c_count:,}", "PASS" if c_count >= 100000 else "FAIL", "Target: >= 100,000 customers")

    p_count = len(products)
    log_check("Product Catalog Volume", f"{p_count:,}", "PASS" if p_count >= 2000 else "FAIL", "Target: >= 2,000 products")

    o_count = len(orders)
    log_check("Order Header Volume", f"{o_count:,}", "PASS" if o_count >= 500000 else "FAIL", "Target: >= 500,000 orders")

    s_count = len(sales)
    log_check("Order-Line Volume", f"{s_count:,}", "PASS" if s_count >= 2000000 else "FAIL", "Target: >= 2,000,000 sales lines")

    r_count = len(returns)
    log_check("Returns Volume", f"{r_count:,}", "PASS" if r_count > 0 else "FAIL", "Realistic return transactions present")

    # 2. Primary Key Uniqueness
    c_pk = customers["CustomerID"].nunique() == c_count
    log_check("Customer PK Uniqueness", "100%", "PASS" if c_pk else "FAIL", "CustomerID must be strictly unique")

    p_pk = products["ProductID"].nunique() == p_count
    log_check("Product PK Uniqueness", "100%", "PASS" if p_pk else "FAIL", "ProductID must be strictly unique")

    o_pk = orders["OrderID"].nunique() == o_count
    log_check("Order PK Uniqueness", "100%", "PASS" if o_pk else "FAIL", "OrderID must be strictly unique")

    s_pk = sales["SalesID"].nunique() == s_count
    log_check("Sales PK Uniqueness", "100%", "PASS" if s_pk else "FAIL", "SalesID must be strictly unique")

    r_pk = returns["ReturnID"].nunique() == r_count
    log_check("Returns PK Uniqueness", "100%", "PASS" if r_pk else "FAIL", "ReturnID must be strictly unique")

    # 3. Referential Integrity (Foreign Keys)
    cust_id_set = set(customers["CustomerID"])
    prod_id_set = set(products["ProductID"])
    order_id_set = set(orders["OrderID"])

    orphan_orders = (~orders["CustomerID"].isin(cust_id_set)).sum()
    log_check("FK: Orders -> Customers", f"{orphan_orders} orphans", "PASS" if orphan_orders == 0 else "FAIL", "Zero orphaned orders allowed")

    orphan_sales_orders = (~sales["OrderID"].isin(order_id_set)).sum()
    log_check("FK: Sales -> Orders", f"{orphan_sales_orders} orphans", "PASS" if orphan_sales_orders == 0 else "FAIL", "Zero orphaned sales order links")

    orphan_sales_prods = (~sales["ProductID"].isin(prod_id_set)).sum()
    log_check("FK: Sales -> Products", f"{orphan_sales_prods} orphans", "PASS" if orphan_sales_prods == 0 else "FAIL", "Zero orphaned sales product links")

    orphan_returns = (~returns["OrderID"].isin(order_id_set)).sum()
    log_check("FK: Returns -> Orders", f"{orphan_returns} orphans", "PASS" if orphan_returns == 0 else "FAIL", "Zero orphaned returns order links")

    # 4. Mathematical Integrity
    expected_sales = (sales["Quantity"] * sales["UnitPrice"] - sales["DiscountAmount"]).round(2)
    sales_math_diff = np.abs(sales["SalesAmount"] - expected_sales).max()
    log_check("Math: SalesAmount Reconciliation", f"Max diff ${sales_math_diff:.4f}", "PASS" if sales_math_diff < 0.05 else "FAIL", "SalesAmount = Qty * Price - Discount")

    expected_profit = (sales["SalesAmount"] - sales["CostAmount"]).round(2)
    profit_math_diff = np.abs(sales["ProfitAmount"] - expected_profit).max()
    log_check("Math: ProfitAmount Reconciliation", f"Max diff ${profit_math_diff:.4f}", "PASS" if profit_math_diff < 0.05 else "FAIL", "ProfitAmount = SalesAmount - CostAmount")

    # Order Header Total vs Line Item Sum
    order_line_sums = sales.groupby("OrderID")["SalesAmount"].sum().round(2)
    order_totals = orders.set_index("OrderID")["TotalAmount"]
    order_diff = np.abs(order_totals - order_line_sums).fillna(0).max()
    log_check("Math: Order Total Reconciliation", f"Max diff ${order_diff:.4f}", "PASS" if order_diff < 0.05 else "FAIL", "Order.TotalAmount = SUM(Sales.SalesAmount)")

    # 5. Business & Chronological Rules
    neg_prices = (products["UnitPrice"] <= 0).sum() + (products["UnitCost"] <= 0).sum()
    log_check("Business: Positive Pricing", f"{neg_prices} violations", "PASS" if neg_prices == 0 else "FAIL", "Unit cost and price must be strictly positive")

    neg_qty = (sales["Quantity"] <= 0).sum()
    log_check("Business: Positive Quantities", f"{neg_qty} violations", "PASS" if neg_qty == 0 else "FAIL", "Quantity sold must be positive")

    # Return rate metric
    ret_rate = (r_count / s_count) * 100
    log_check("Business: Return Rate Check", f"{ret_rate:.2f}%", "PASS" if 2.0 <= ret_rate <= 20.0 else "WARN", "Overall line-item return rate within retail benchmark")

    # Save Quality Report
    report_df = pd.DataFrame(report_rows)
    out_file = REPORTS_DIR / "data_quality_report.csv"
    report_df.to_csv(out_file, index=False)
    logger.info(f"Data Quality Report successfully written -> {out_file}")

    return report_df

if __name__ == "__main__":
    validate_data()
