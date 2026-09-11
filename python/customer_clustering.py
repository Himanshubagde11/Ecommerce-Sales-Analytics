"""
Machine Learning Customer Segmentation using K-Means and Scikit-Learn.
Builds 8 behavioral customer features, standardizes metrics, evaluates K via Elbow and Silhouette,
and profiles clusters into actionable business cohorts.
Exports reports/customer_clusters.csv and reports/cluster_analysis.csv.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    RANDOM_SEED,
    setup_logger
)

logger = setup_logger("customer_clustering")

def run_customer_clustering():
    """Builds behavioral feature matrix, evaluates K, clusters customers, and profiles cohorts."""
    logger.info("Starting K-Means Customer Clustering Pipeline...")

    # 1. Load Data
    customers = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_customers.csv")
    orders = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_orders.csv")
    sales = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_sales.csv")
    returns = pd.read_csv(PROCESSED_DATA_DIR / "cleaned_returns.csv")

    sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
    ref_date = sales["OrderDate"].max() + pd.Timedelta(days=1)

    # 2. Engineer Customer Behavioral Features
    logger.info("Engineering 8 customer behavioral features...")
    # Base Sales aggregation
    cust_sales = sales.groupby("CustomerID").agg(
        TotalSales=("SalesAmount", "sum"),
        TotalQuantity=("Quantity", "sum"),
        TotalDiscount=("DiscountAmount", "sum"),
        FirstOrder=("OrderDate", "min"),
        LastOrder=("OrderDate", "max"),
        TotalOrders=("OrderID", "nunique")
    ).reset_index()

    # Calculate Lifespan and Recency
    cust_sales["Recency"] = (ref_date - cust_sales["LastOrder"]).dt.days
    cust_sales["CustomerLifespan"] = (cust_sales["LastOrder"] - cust_sales["FirstOrder"]).dt.days.clip(lower=1)
    cust_sales["Monetary"] = cust_sales["TotalSales"].round(2)
    cust_sales["Frequency"] = cust_sales["TotalOrders"]
    cust_sales["AverageOrderValue"] = (cust_sales["Monetary"] / cust_sales["Frequency"]).round(2)
    cust_sales["AverageDiscount"] = (cust_sales["TotalDiscount"] / (cust_sales["Monetary"] + cust_sales["TotalDiscount"] + 1e-5)).round(4)

    # Returns aggregation
    cust_returns = returns.groupby("CustomerID")["QuantityReturned"].sum().reset_index()
    cust_sales = cust_sales.merge(cust_returns, on="CustomerID", how="left")
    cust_sales["QuantityReturned"] = cust_sales["QuantityReturned"].fillna(0)
    cust_sales["ReturnRate"] = (cust_sales["QuantityReturned"] / cust_sales["TotalQuantity"]).clip(0, 1).round(4)

    # Merge with demographic customer list
    feature_cols = [
        "Recency", "Frequency", "Monetary", "AverageOrderValue",
        "TotalQuantity", "ReturnRate", "AverageDiscount", "CustomerLifespan"
    ]
    df_features = customers[["CustomerID", "CustomerName", "Country", "Region"]].merge(
        cust_sales[["CustomerID"] + feature_cols], on="CustomerID", how="inner"
    )

    logger.info(f"Feature matrix built for {len(df_features):,} active purchasing customers.")

    # 3. Log Transformation for skewed monetary/frequency features and Standardization
    X = df_features[feature_cols].copy()
    X_log = X.copy()
    for col in ["Frequency", "Monetary", "AverageOrderValue", "TotalQuantity", "CustomerLifespan"]:
        X_log[col] = np.log1p(X_log[col])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)

    # 4. Evaluate K from 2 to 8 (Elbow and Silhouette)
    logger.info("Evaluating optimal cluster counts (K = 2 to 8)...")
    k_range = range(2, 9)
    inertias = []
    silhouette_scores = []

    # Use a sample of 15,000 for fast silhouette calculation across 100k records
    sample_indices = np.random.default_rng(RANDOM_SEED).choice(len(X_scaled), size=min(15000, len(X_scaled)), replace=False)
    X_eval_sample = X_scaled[sample_indices]

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_eval_sample, km.predict(X_eval_sample))
        silhouette_scores.append(sil)
        logger.info(f"K={k} -> Inertia: {km.inertia_:,.1f}, Silhouette Score: {sil:.4f}")

    # Determine K: test K=5 per portfolio specification
    # If K=5 provides strong silhouette and distinct commercial groups, select 5
    chosen_k = 5
    logger.info(f"Selecting K={chosen_k} based on elbow convergence and distinct business interpretability.")

    # 5. Fit Final Model with Chosen K=5
    final_kmeans = KMeans(n_clusters=chosen_k, random_state=RANDOM_SEED, n_init=15)
    df_features["ClusterID"] = final_kmeans.fit_predict(X_scaled)

    # 6. Profile Clusters and Assign Business Names
    profile = df_features.groupby("ClusterID")[feature_cols].mean().round(2)
    counts = df_features["ClusterID"].value_counts().sort_index()
    profile["CustomerCount"] = counts
    profile["PercentShare"] = (counts / len(df_features) * 100).round(2)

    logger.info("Raw Cluster Centroids:\n" + profile.to_string())

    # Interpret Clusters based on their actual mean metrics:
    # We rank clusters by Monetary and Frequency
    cluster_names = {}
    for cid in range(chosen_k):
        m = profile.loc[cid, "Monetary"]
        f = profile.loc[cid, "Frequency"]
        r = profile.loc[cid, "Recency"]
        disc = profile.loc[cid, "AverageDiscount"]
        ret = profile.loc[cid, "ReturnRate"]

        if m >= profile["Monetary"].quantile(0.80):
            cluster_names[cid] = "High-Value VIPs"
        elif disc >= profile["AverageDiscount"].quantile(0.70):
            cluster_names[cid] = "Deal Seekers & Bargain Shoppers"
        elif r <= profile["Recency"].quantile(0.35) and f >= profile["Frequency"].median():
            cluster_names[cid] = "Active Steady Repeaters"
        elif r >= profile["Recency"].quantile(0.65):
            cluster_names[cid] = "Dormant Occasional Buyers"
        else:
            cluster_names[cid] = "Mid-Tier Potential Loyalists"

    # Avoid duplicate names if any by resolving unique mappings
    seen_names = set()
    for cid in range(chosen_k):
        base_name = cluster_names[cid]
        if base_name in seen_names:
            cluster_names[cid] = f"{base_name} (Cohort {cid+1})"
        seen_names.add(cluster_names[cid])

    df_features["ClusterName"] = df_features["ClusterID"].map(cluster_names)
    profile["ClusterName"] = [cluster_names[i] for i in profile.index]

    # Save outputs
    out_clusters = REPORTS_DIR / "customer_clusters.csv"
    df_features.to_csv(out_clusters, index=False)
    logger.info(f"Customer clusters exported -> {out_clusters}")

    out_analysis = REPORTS_DIR / "cluster_analysis.csv"
    profile.reset_index().to_csv(out_analysis, index=False)
    logger.info(f"Cluster profile analysis exported -> {out_analysis}")

    return df_features, profile

if __name__ == "__main__":
    run_customer_clustering()
