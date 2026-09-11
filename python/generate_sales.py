"""
Vectorized generation of 2,000,000+ order-line transaction records for Veyra E-Commerce.
Ensures exact financial reconciliation:
SalesAmount = Quantity * UnitPrice - DiscountAmount
CostAmount = Quantity * UnitCost
ProfitAmount = SalesAmount - CostAmount
And reconciles Order TotalAmount = SUM(SalesAmount).
"""

import numpy as np
import pandas as pd
from config import (
    RAW_DATA_DIR,
    NUM_ORDERS,
    TARGET_SALES_RECORDS,
    RANDOM_SEED,
    setup_logger
)

logger = setup_logger("generate_sales")

def generate_sales(target_records: int = TARGET_SALES_RECORDS) -> pd.DataFrame:
    """Generates 2,000,000+ order-line items linked to orders and products with strict math integrity."""
    logger.info(f"Generating {target_records:,}+ order-line transaction records...")
    rng = np.random.default_rng(RANDOM_SEED)

    # 1. Load Orders and Products metadata
    orders_file = RAW_DATA_DIR / "orders.csv"
    products_file = RAW_DATA_DIR / "products.csv"

    if not orders_file.exists():
        from generate_orders import generate_orders
        orders_df = generate_orders()
    else:
        orders_df = pd.read_csv(orders_file, usecols=["OrderID", "CustomerID", "OrderDate", "Discount"])

    if not products_file.exists():
        from generate_products import generate_products
        products_df = generate_products()
    else:
        products_df = pd.read_csv(products_file, usecols=["ProductID", "CategoryID", "UnitCost", "UnitPrice"])

    num_orders = len(orders_df)
    order_ids = orders_df["OrderID"].values
    cust_ids = orders_df["CustomerID"].values
    order_dates = orders_df["OrderDate"].values
    order_discounts = orders_df["Discount"].values

    prod_ids = products_df["ProductID"].values
    prod_costs = products_df["UnitCost"].values
    prod_prices = products_df["UnitPrice"].values
    prod_cats = products_df["CategoryID"].values

    # Category popularity weights (e.g., Electronics & Fashion have higher purchase counts)
    cat_weights = {1: 0.18, 2: 0.22, 3: 0.14, 4: 0.12, 5: 0.08, 6: 0.07, 7: 0.06, 8: 0.05, 9: 0.03, 10: 0.05}
    prod_prob = np.array([cat_weights[c] for c in prod_cats])
    prod_prob = prod_prob / prod_prob.sum()

    # 2. Determine basket size per order (mean ~ 4.2 items -> 500k orders * 4.2 = ~2.1M lines)
    # Use clipped Poisson / geometric distribution
    basket_sizes = rng.poisson(lam=3.2, size=num_orders) + 1  # 1 to 10 items, min 1
    total_generated_lines = np.sum(basket_sizes)
    logger.info(f"Allocated {total_generated_lines:,} total order-line items across {num_orders:,} orders.")

    # Repeat order metadata across basket items
    rep_order_ids = np.repeat(order_ids, basket_sizes)
    rep_cust_ids = np.repeat(cust_ids, basket_sizes)
    rep_order_dates = np.repeat(order_dates, basket_sizes)
    rep_order_discounts = np.repeat(order_discounts, basket_sizes)

    # 3. Sample Product IDs
    chosen_prod_indices = rng.choice(len(prod_ids), size=total_generated_lines, p=prod_prob)
    chosen_prod_ids = prod_ids[chosen_prod_indices]
    chosen_unit_costs = prod_costs[chosen_prod_indices]
    chosen_unit_prices = prod_prices[chosen_prod_indices]

    # 4. Item Quantities: 1 (72%), 2 (19%), 3 (6%), 4 (2%), 5 (1%)
    quantities = rng.choice([1, 2, 3, 4, 5], size=total_generated_lines, p=[0.72, 0.19, 0.06, 0.02, 0.01])

    # 5. Financial Calculations:
    # Promotional line-item discount variation
    item_promo_factor = rng.choice([0.0, 0.05, 0.10, 0.15], size=total_generated_lines, p=[0.60, 0.25, 0.10, 0.05])
    # Combined effective discount rate capped at 35%
    effective_discount_rate = np.clip(rep_order_discounts + item_promo_factor, 0.0, 0.35)

    gross_amounts = quantities * chosen_unit_prices
    discount_amounts = np.round(gross_amounts * effective_discount_rate, 2)
    sales_amounts = np.round(gross_amounts - discount_amounts, 2)
    cost_amounts = np.round(quantities * chosen_unit_costs, 2)
    profit_amounts = np.round(sales_amounts - cost_amounts, 2)

    sales_ids = np.arange(1, total_generated_lines + 1)

    sales_df = pd.DataFrame({
        "SalesID": sales_ids,
        "OrderID": rep_order_ids,
        "CustomerID": rep_cust_ids,
        "ProductID": chosen_prod_ids,
        "OrderDate": rep_order_dates,
        "Quantity": quantities,
        "UnitPrice": chosen_unit_prices,
        "DiscountAmount": discount_amounts,
        "SalesAmount": sales_amounts,
        "CostAmount": cost_amounts,
        "ProfitAmount": profit_amounts
    })

    out_file = RAW_DATA_DIR / "sales.csv"
    sales_df.to_csv(out_file, index=False)
    logger.info(f"Successfully generated {len(sales_df):,} order lines -> {out_file}")

    # 6. Reconcile TotalAmount in orders.csv
    logger.info("Reconciling TotalAmount in orders.csv to match exact SUM(SalesAmount)...")
    order_totals = sales_df.groupby("OrderID")["SalesAmount"].sum().reset_index()
    order_totals.rename(columns={"SalesAmount": "CalculatedTotal"}, inplace=True)

    # Read full orders.csv and merge
    full_orders_df = pd.read_csv(orders_file)
    full_orders_df.drop(columns=["TotalAmount"], errors="ignore", inplace=True)
    full_orders_df = full_orders_df.merge(order_totals, on="OrderID", how="left")
    full_orders_df["TotalAmount"] = np.round(full_orders_df["CalculatedTotal"].fillna(0.0), 2)
    full_orders_df.drop(columns=["CalculatedTotal"], inplace=True)
    
    full_orders_df.to_csv(orders_file, index=False)
    logger.info("Successfully updated orders.csv with exact reconciled TotalAmount values.")

    return sales_df

if __name__ == "__main__":
    generate_sales()
