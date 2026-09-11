"""
Configuration and constants for the VEYRA E-Commerce Sales Analytics project.
Reproducible seed, paths, business rules, category parameters, and logging setup.
"""

import os
import logging
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
REPORTS_DIR = BASE_DIR / "reports"
EXCEL_DIR = BASE_DIR / "excel"
SQL_DIR = BASE_DIR / "sql"
DOCS_DIR = BASE_DIR / "docs"
POWERBI_DIR = BASE_DIR / "powerbi"

# Ensure all target directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLE_DATA_DIR, REPORTS_DIR, EXCEL_DIR, SQL_DIR, DOCS_DIR, POWERBI_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Random Seed for 100% Reproducibility
RANDOM_SEED = 42

# Dataset Scale
NUM_CUSTOMERS = 100000       # 100k+
NUM_PRODUCTS = 2000          # 2k+
NUM_ORDERS = 500000          # 500k+
TARGET_SALES_RECORDS = 2000000  # 2M+ order line records

# Time Horizon
START_DATE = "2022-01-01"
END_DATE = "2025-12-31"

# Product Categories and Pricing Profiles (Cost range & Target Margin)
CATEGORIES = {
    1: {"name": "Electronics", "cost_min": 40.0, "cost_max": 950.0, "margin_min": 0.22, "margin_max": 0.38, "return_rate": 0.09},
    2: {"name": "Fashion", "cost_min": 12.0, "cost_max": 180.0, "margin_min": 0.50, "margin_max": 0.70, "return_rate": 0.19},
    3: {"name": "Home & Kitchen", "cost_min": 15.0, "cost_max": 350.0, "margin_min": 0.40, "margin_max": 0.58, "return_rate": 0.07},
    4: {"name": "Beauty", "cost_min": 8.0, "cost_max": 130.0, "margin_min": 0.55, "margin_max": 0.75, "return_rate": 0.04},
    5: {"name": "Sports & Fitness", "cost_min": 20.0, "cost_max": 450.0, "margin_min": 0.35, "margin_max": 0.52, "return_rate": 0.08},
    6: {"name": "Grocery", "cost_min": 2.5, "cost_max": 45.0, "margin_min": 0.15, "margin_max": 0.25, "return_rate": 0.02},
    7: {"name": "Books", "cost_min": 4.0, "cost_max": 55.0, "margin_min": 0.30, "margin_max": 0.50, "return_rate": 0.04},
    8: {"name": "Accessories", "cost_min": 6.0, "cost_max": 140.0, "margin_min": 0.50, "margin_max": 0.68, "return_rate": 0.08},
    9: {"name": "Furniture", "cost_min": 85.0, "cost_max": 1250.0, "margin_min": 0.35, "margin_max": 0.52, "return_rate": 0.06},
    10: {"name": "Toys", "cost_min": 7.0, "cost_max": 110.0, "margin_min": 0.40, "margin_max": 0.60, "return_rate": 0.06}
}

# Customer Acquisition Channels
ACQUISITION_CHANNELS = [
    "Organic Search",
    "Paid Search",
    "Social Media",
    "Email",
    "Referral",
    "Direct",
    "Affiliate"
]
ACQUISITION_WEIGHTS = [0.25, 0.20, 0.22, 0.12, 0.08, 0.08, 0.05]

# Order Statuses
ORDER_STATUSES = ["Delivered", "Cancelled", "Returned", "Pending"]
ORDER_STATUS_WEIGHTS = [0.88, 0.05, 0.05, 0.02]

# Payment Methods
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet", "COD"]
PAYMENT_WEIGHTS = [0.38, 0.22, 0.18, 0.10, 0.07, 0.05]

# Shipping Methods
SHIPPING_METHODS = ["Standard Shipping", "Express Shipping", "Priority Overnight", "Economy Shipping"]
SHIPPING_WEIGHTS = [0.55, 0.28, 0.10, 0.07]

# Return Reasons
RETURN_REASONS = [
    "Size Issue",
    "Damaged",
    "Quality Issue",
    "Customer Changed Mind",
    "Wrong Product",
    "Late Delivery",
    "Other"
]
RETURN_REASON_WEIGHTS = [0.32, 0.20, 0.18, 0.14, 0.08, 0.05, 0.03]

# SQL Server Configuration
SQL_SERVER_CONFIG = {
    "server": os.getenv("VEYRA_SQL_SERVER", "localhost"),
    "database": os.getenv("VEYRA_SQL_DB", "VeyraDW"),
    "driver": os.getenv("VEYRA_SQL_DRIVER", "ODBC Driver 17 for SQL Server"),
    "trusted_connection": os.getenv("VEYRA_SQL_TRUSTED", "yes"),
    "username": os.getenv("VEYRA_SQL_USER", "sa"),
    "password": os.getenv("VEYRA_SQL_PWD", "")
}

def setup_logger(name: str = "veyra_pipeline") -> logging.Logger:
    """Configures a standardized console and file logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        log_file = BASE_DIR / "pipeline.log"
        fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
