import pyodbc
import pandas as pd
import json

conn_str = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=VeyraDW;Trusted_Connection=yes;TrustServerCertificate=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def get_scalar(sql):
    cursor.execute(sql)
    return cursor.fetchone()[0]

results = {}

tables = [
    'dw.DimCategory',
    'dw.DimProduct',
    'dw.DimLocation',
    'dw.DimCustomer',
    'dw.DimPayment',
    'dw.DimDate',
    'dw.FactSales',
    'dw.FactReturns'
]

print("====================================================")
print("  VEYRADW DATABASE VERIFICATION & AUDIT")
print("====================================================")

for t in tables:
    cnt = get_scalar(f"SELECT COUNT(1) FROM {t}")
    results[t] = cnt
    print(f"{t:<20}: {cnt:>12,}")

orders_cnt = get_scalar("SELECT COUNT(DISTINCT OrderID) FROM dw.FactSales")
results['DistinctOrders'] = orders_cnt
print(f"{'Distinct Orders':<20}: {orders_cnt:>12,}")

purchasing_cust = get_scalar("SELECT COUNT(DISTINCT CustomerKey) FROM dw.FactSales")
results['PurchasingCustomers'] = purchasing_cust
print(f"{'Active Customers':<20}: {purchasing_cust:>12,}")

views = [
    'analytics.vw_MonthlySales',
    'analytics.vw_CategoryPerformance',
    'analytics.vw_ProductPerformance',
    'analytics.vw_CustomerValue',
    'analytics.vw_RegionalPerformance',
    'analytics.vw_RFMCustomer',
    'analytics.vw_CustomerChurn',
    'analytics.vw_CLV'
]

print("\n====================================================")
print("  POWER BI PRESENTATION VIEWS VERIFICATION")
print("====================================================")

view_results = {}
for v in views:
    cnt = get_scalar(f"SELECT COUNT(1) FROM {v}")
    view_results[v] = cnt
    print(f"{v:<35}: {cnt:>10,} rows")

# K-Means segmentation validation
print("\n====================================================")
print("  MACHINE LEARNING & CUSTOMER SEGMENTATION AUDIT")
print("====================================================")

try:
    df_cluster = pd.read_csv('reports/customer_clusters.csv')
    cluster_count = df_cluster['ClusterID'].nunique()
    cluster_records = len(df_cluster)
    print(f"{'K-Means Clusters':<35}: {cluster_count} distinct clusters")
    print(f"{'Clustered Customers':<35}: {cluster_records:>10,} rows")
    print(df_cluster['ClusterName'].value_counts())
except Exception as e:
    print(f"Cluster CSV notice: {e}")

# High level KPI checks
print("\n====================================================")
print("  CORE BUSINESS METRICS SAMPLE")
print("====================================================")
cursor.execute("""
SELECT 
    SUM(SalesAmount) AS TotalRevenue,
    SUM(ProfitAmount) AS TotalProfit,
    ROUND(SUM(ProfitAmount) / NULLIF(SUM(SalesAmount), 0) * 100, 2) AS MarginPct,
    ROUND(SUM(SalesAmount) / NULLIF(COUNT(DISTINCT OrderID), 0), 2) AS AOV
FROM dw.FactSales
""")
kpi = cursor.fetchone()
print(f"Total Revenue:  ${kpi[0]:,.2f}")
print(f"Total Profit:   ${kpi[1]:,.2f}")
print(f"Profit Margin:  {kpi[2]}%")
print(f"Average AOV:    ${kpi[3]:,.2f}")

conn.close()
