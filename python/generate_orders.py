"""
Vectorized generation of 500,000+ realistic orders for Veyra E-Commerce.
Includes realistic customer purchasing power-law, seasonality (Q4 peaks, Black Friday),
and strict chronological validity (OrderDate >= SignupDate).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config import (
    RAW_DATA_DIR,
    NUM_ORDERS,
    RANDOM_SEED,
    ORDER_STATUSES,
    ORDER_STATUS_WEIGHTS,
    PAYMENT_METHODS,
    PAYMENT_WEIGHTS,
    SHIPPING_METHODS,
    SHIPPING_WEIGHTS,
    setup_logger
)

logger = setup_logger("generate_orders")

def generate_orders(num_orders: int = NUM_ORDERS) -> pd.DataFrame:
    """Generates order headers with customer linkages, seasonal date patterns, and shipping details."""
    logger.info(f"Generating {num_orders:,} order header records...")
    rng = np.random.default_rng(RANDOM_SEED)

    # 1. Load customers to ensure referential integrity and valid dates
    cust_file = RAW_DATA_DIR / "customers.csv"
    if not cust_file.exists():
        from generate_customers import generate_customers
        customers_df = generate_customers()
    else:
        customers_df = pd.read_csv(cust_file, usecols=["CustomerID", "SignupDate"])

    num_customers = len(customers_df)
    customer_ids = customers_df["CustomerID"].values
    signup_dates = pd.to_datetime(customers_df["SignupDate"]).values

    # 2. Build Customer Purchase Activity Distribution (Power-law / Negative Binomial)
    # Some customers buy 1 time, others buy 2-5, VIPs buy up to 25+
    cust_weights = rng.gamma(shape=0.6, scale=2.5, size=num_customers)
    cust_weights = cust_weights / cust_weights.sum()

    chosen_cust_indices = rng.choice(num_customers, size=num_orders, p=cust_weights)
    order_customer_ids = customer_ids[chosen_cust_indices]
    cust_signups = signup_dates[chosen_cust_indices]

    # 3. Calendar & Seasonal Date Generation across 2022-01-01 to 2025-12-31
    all_dates = pd.date_range("2022-01-01", "2025-12-31", freq='D')
    days_count = len(all_dates)

    # Base monthly seasonality factors
    month_factors = {
        1: 0.90, 2: 0.85, 3: 0.95, 4: 0.95, 5: 1.00, 6: 1.05,
        7: 1.10, 8: 1.05, 9: 1.02, 10: 1.15, 11: 1.55, 12: 1.65
    }
    # YoY enterprise growth factors
    year_factors = {2022: 1.00, 2023: 1.18, 2024: 1.38, 2025: 1.55}

    day_weights = np.zeros(days_count)
    for idx, dt in enumerate(all_dates):
        m_weight = month_factors[dt.month]
        y_weight = year_factors[dt.year]
        # Day of week boost (Weekend & Monday shopping)
        dow_boost = 1.12 if dt.weekday() in [0, 5, 6] else 0.96
        # Specific shopping spikes: Black Friday (late Nov) & Cyber Monday
        spike = 1.0
        if dt.month == 11 and 23 <= dt.day <= 29:
            spike = 2.2 # Black Friday / Cyber Monday surge
        elif dt.month == 12 and 12 <= dt.day <= 23:
            spike = 1.8 # Holiday shopping frenzy
        elif dt.month == 7 and 10 <= dt.day <= 15:
            spike = 1.4 # Mid-year Summer Mega Sale
        
        day_weights[idx] = m_weight * y_weight * dow_boost * spike

    day_weights = day_weights / day_weights.sum()

    # Sample order dates according to seasonal curve
    chosen_date_indices = rng.choice(days_count, size=num_orders, p=day_weights)
    raw_order_dates = all_dates[chosen_date_indices].values.copy()

    # Guarantee OrderDate >= SignupDate
    cust_signups_ns = cust_signups.astype('datetime64[ns]')
    raw_order_dates_ns = raw_order_dates.astype('datetime64[ns]')
    end_date_ns = np.datetime64("2025-12-31T23:59:59", "ns")

    needs_adjustment = raw_order_dates_ns < cust_signups_ns
    if np.any(needs_adjustment):
        signup_int = cust_signups_ns[needs_adjustment].astype('int64')
        end_int = end_date_ns.astype('int64')
        valid_range = np.maximum(end_int - signup_int, 86400 * 10**9)
        new_ts = signup_int + (rng.uniform(0, 1, size=np.sum(needs_adjustment)) * valid_range).astype('int64')
        raw_order_dates_ns[needs_adjustment] = new_ts.astype('datetime64[ns]')

    # Convert to standard daily date format
    order_dates_dt = pd.to_datetime(raw_order_dates_ns).normalize()

    # 4. Shipping & Delivery Dates
    # Shipping takes 1 to 3 days
    ship_delay_days = rng.choice([1, 2, 3], size=num_orders, p=[0.50, 0.35, 0.15])
    shipping_dates_dt = order_dates_dt + pd.to_timedelta(ship_delay_days, unit='D')

    # Delivery takes 2 to 5 days after shipping
    delivery_delay_days = rng.choice([2, 3, 4, 5], size=num_orders, p=[0.40, 0.35, 0.15, 0.10])
    delivery_dates_dt = shipping_dates_dt + pd.to_timedelta(delivery_delay_days, unit='D')

    # 5. Order Status, Payment & Shipping Methods
    order_statuses = rng.choice(ORDER_STATUSES, size=num_orders, p=ORDER_STATUS_WEIGHTS)
    payment_methods = rng.choice(PAYMENT_METHODS, size=num_orders, p=PAYMENT_WEIGHTS)
    shipping_methods = rng.choice(SHIPPING_METHODS, size=num_orders, p=SHIPPING_WEIGHTS)

    # Discounts at Order level (0%, 5%, 10%, 15%, 20%)
    order_discounts = rng.choice([0.0, 0.05, 0.10, 0.15, 0.20], size=num_orders, p=[0.50, 0.22, 0.15, 0.08, 0.05])

    # Date string formatting and status handling
    order_date_strs = order_dates_dt.strftime('%Y-%m-%d').to_numpy()
    shipping_date_strs = shipping_dates_dt.strftime('%Y-%m-%d').to_numpy(dtype=object)
    delivery_date_strs = delivery_dates_dt.strftime('%Y-%m-%d').to_numpy(dtype=object)

    # Cancelled orders have no shipping or delivery date
    cancelled_mask = (order_statuses == "Cancelled")
    shipping_date_strs[cancelled_mask] = None
    delivery_date_strs[cancelled_mask] = None

    # Pending orders have no delivery date, and might not have shipped yet
    pending_mask = (order_statuses == "Pending")
    shipping_date_strs[pending_mask] = None
    delivery_date_strs[pending_mask] = None

    order_ids = np.arange(1, num_orders + 1)

    df = pd.DataFrame({
        "OrderID": order_ids,
        "CustomerID": order_customer_ids,
        "OrderDate": order_date_strs,
        "ShippingDate": shipping_date_strs,
        "DeliveryDate": delivery_date_strs,
        "OrderStatus": order_statuses,
        "PaymentMethod": payment_methods,
        "ShippingMethod": shipping_methods,
        "Discount": order_discounts,
        "TotalAmount": 0.0  # Will be reconciled exactly after Sales line generation
    })

    out_file = RAW_DATA_DIR / "orders.csv"
    df.to_csv(out_file, index=False)
    logger.info(f"Successfully generated {len(df):,} orders -> {out_file}")
    return df

if __name__ == "__main__":
    generate_orders()
