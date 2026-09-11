"""
Vectorized generation of realistic returns dataset for Veyra E-Commerce.
Includes category-dependent return probabilities, realistic return reasons,
and valid chronological return dates.
"""

import numpy as np
import pandas as pd
from config import (
    RAW_DATA_DIR,
    RANDOM_SEED,
    CATEGORIES,
    RETURN_REASONS,
    RETURN_REASON_WEIGHTS,
    setup_logger
)

logger = setup_logger("generate_returns")

def generate_returns() -> pd.DataFrame:
    """Generates returns linked to delivered and returned orders with category-specific return rates."""
    logger.info("Generating realistic product return records...")
    rng = np.random.default_rng(RANDOM_SEED)

    # 1. Load Sales, Orders, Products
    sales_file = RAW_DATA_DIR / "sales.csv"
    orders_file = RAW_DATA_DIR / "orders.csv"
    products_file = RAW_DATA_DIR / "products.csv"

    if not sales_file.exists():
        from generate_sales import generate_sales
        sales_df = generate_sales()
    else:
        sales_df = pd.read_csv(sales_file)

    orders_df = pd.read_csv(orders_file, usecols=["OrderID", "OrderStatus", "DeliveryDate"])
    products_df = pd.read_csv(products_file, usecols=["ProductID", "CategoryID"])

    # Merge product category and order status into sales
    merged = sales_df.merge(orders_df, on="OrderID", how="inner")
    merged = merged.merge(products_df, on="ProductID", how="inner")

    # Exclude Cancelled and Pending orders from returns
    eligible = merged[merged["OrderStatus"].isin(["Delivered", "Returned"])].copy()

    # Category return rates
    cat_return_rates = {cat_id: cfg["return_rate"] for cat_id, cfg in CATEGORIES.items()}
    prob_series = eligible["CategoryID"].map(cat_return_rates).fillna(0.05).values

    # If order status is explicitly "Returned", probability is 1.0; otherwise category return rate
    is_order_returned = (eligible["OrderStatus"].values == "Returned")
    effective_probs = np.where(is_order_returned, 1.0, prob_series)

    # Simulate return trigger
    random_draws = rng.uniform(0.0, 1.0, size=len(eligible))
    return_mask = random_draws < effective_probs

    returned_items = eligible[return_mask].copy()
    num_returns = len(returned_items)
    logger.info(f"Identified {num_returns:,} return transactions out of {len(eligible):,} eligible sales lines.")

    # Generate Return Reasons
    # Size Issue is heavily concentrated in Fashion
    fashion_mask = (returned_items["CategoryID"].values == 2)
    reasons = np.empty(num_returns, dtype=object)
    
    # Non-fashion reason weights
    non_fashion_weights = [0.05, 0.28, 0.25, 0.22, 0.10, 0.07, 0.03]
    # Fashion reason weights (Size issue dominates)
    fashion_weights = [0.55, 0.10, 0.12, 0.12, 0.06, 0.03, 0.02]

    if np.any(fashion_mask):
        reasons[fashion_mask] = rng.choice(RETURN_REASONS, size=np.sum(fashion_mask), p=fashion_weights)
    if np.any(~fashion_mask):
        reasons[~fashion_mask] = rng.choice(RETURN_REASONS, size=np.sum(~fashion_mask), p=non_fashion_weights)

    # Return Dates: DeliveryDate + 2 to 14 days (or OrderDate + 5 to 18 days if DeliveryDate is null)
    base_dates = pd.to_datetime(returned_items["DeliveryDate"].fillna(returned_items["OrderDate"]))
    return_delay = rng.choice(np.arange(2, 15), size=num_returns)
    return_dates = base_dates + pd.to_timedelta(return_delay, unit='D')
    return_date_strs = return_dates.dt.strftime('%Y-%m-%d')

    # Quantities and Return Amount
    sold_qty = returned_items["Quantity"].values
    sales_amt = returned_items["SalesAmount"].values
    # Full return for 90%, partial for 10% where qty > 1
    partial_mask = (sold_qty > 1) & (rng.uniform(0, 1, size=num_returns) < 0.15)
    ret_qty = sold_qty.copy()
    ret_qty[partial_mask] = np.maximum(1, sold_qty[partial_mask] - 1)

    unit_effective_price = sales_amt / sold_qty
    ret_amt = np.round(ret_qty * unit_effective_price, 2)

    return_ids = np.arange(1, num_returns + 1)

    returns_df = pd.DataFrame({
        "ReturnID": return_ids,
        "OrderID": returned_items["OrderID"].values,
        "CustomerID": returned_items["CustomerID"].values,
        "ProductID": returned_items["ProductID"].values,
        "ReturnDate": return_date_strs.values,
        "QuantityReturned": ret_qty,
        "ReturnAmount": ret_amt,
        "ReturnReason": reasons
    })

    out_file = RAW_DATA_DIR / "returns.csv"
    returns_df.to_csv(out_file, index=False)
    logger.info(f"Successfully generated {len(returns_df):,} return records -> {out_file}")
    return returns_df

if __name__ == "__main__":
    generate_returns()
