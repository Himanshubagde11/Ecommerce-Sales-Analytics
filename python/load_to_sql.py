"""
SQL Server Data Loading Utility for Veyra E-Commerce.
Loads staging tables (stg.Customers, stg.Products, stg.Orders, stg.Sales, stg.Returns)
into SQL Server using SQLAlchemy and fast_executemany.
Provides connection diagnostics and graceful fallback instructions.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from config import (
    PROCESSED_DATA_DIR,
    SQL_SERVER_CONFIG,
    setup_logger
)

logger = setup_logger("load_to_sql")

def get_sql_server_engine():
    """Builds a SQLAlchemy engine for SQL Server based on configuration."""
    cfg = SQL_SERVER_CONFIG
    server = cfg["server"]
    db = cfg["database"]
    driver = cfg["driver"]

    # Try trusted connection first, otherwise SQL authentication
    if cfg.get("trusted_connection", "yes").lower() in ["yes", "true", "1"]:
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db};Trusted_Connection=yes;"
    else:
        user = cfg["username"]
        pwd = cfg["password"]
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db};UID={user};PWD={pwd};"

    quoted_conn_str = quote_plus(conn_str)
    engine_url = f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}"
    
    return create_engine(engine_url, fast_executemany=True)

def test_connection():
    """Tests connectivity to SQL Server."""
    try:
        engine = get_sql_server_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION;")).scalar()
            logger.info(f"Connected to SQL Server successfully:\n{result}")
            return True, engine
    except Exception as e:
        logger.warning(f"Could not connect to SQL Server: {e}")
        logger.info("To connect: Ensure SQL Server is running, database 'VeyraDW' is created, and connection parameters in python/config.py match your instance.")
        return False, None

def load_staging_tables(engine=None, chunk_size: int = 50000):
    """Loads processed CSVs into staging tables in SQL Server."""
    if engine is None:
        connected, engine = test_connection()
        if not connected:
            logger.error("SQL Server instance is not currently accessible. Staging load aborted.")
            return False

    tables = [
        ("cleaned_customers.csv", "Customers", "stg"),
        ("cleaned_products.csv", "Products", "stg"),
        ("cleaned_orders.csv", "Orders", "stg"),
        ("cleaned_sales.csv", "Sales", "stg"),
        ("cleaned_returns.csv", "Returns", "stg")
    ]

    for file_name, table_name, schema in tables:
        file_path = PROCESSED_DATA_DIR / file_name
        if not file_path.exists():
            logger.warning(f"File {file_path} not found. Skipping {schema}.{table_name}.")
            continue

        logger.info(f"Loading {file_path.name} into [{schema}].[{table_name}] (chunk size: {chunk_size:,})...")
        
        # Load in chunks to manage memory
        for chunk_idx, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
            if_exists_behavior = "replace" if chunk_idx == 0 else "append"
            chunk.to_sql(
                name=table_name,
                con=engine,
                schema=schema,
                if_exists=if_exists_behavior,
                index=False
            )
            logger.info(f"  Inserted chunk {chunk_idx + 1} (rows: {len(chunk):,})")

        logger.info(f"Finished loading [{schema}].[{table_name}].")

    return True

if __name__ == "__main__":
    test_connection()
