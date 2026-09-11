# Power BI Dashboard UI/UX Design System: VEYRA E-Commerce

## 1. Executive Design Language & Palette

The dashboard utilizes an enterprise dark theme designed for modern C-suite analytics. It avoids generic out-of-the-box Power BI visuals in favor of clean card containers, consistent typography, and high-contrast accessibility.

```
[ Canvas Background: #111418 ]
  │
  ├── [ Card Container: #1F242D | Border: 1px #2A303C | Corner Radius: 8px ]
  │     ├── [ Primary Text: #FFFFFF (Segoe UI / DIN) ]
  │     ├── [ Secondary Label: #9E9E9E (10pt Regular) ]
  │     └── [ Primary Accent: #FF6B00 (Veyra Orange) ]
  │
  ├── [ Success KPI: #10B981 (Emerald Green) ]
  └── [ Hazard / Churn KPI: #EF4444 (Crimson Red) ]
```

---

## 2. Global Canvas & Component Specifications
- **Canvas Size**: 16:9 Widescreen (`1920 x 1080 px`).
- **Header Banner**: Height `70 px`, Background `#161B22`. Includes Veyra logo, active page title, global currency notification (USD), and last refresh timestamp.
- **Top Filter Slicer Bar**: Height `65 px`. Contains interactive dropdown slicers for:
  - `Date Range` (Relative Date / Between Slider)
  - `Product Category` (Multi-select)
  - `Global Region` (Multi-select)
  - `Customer Segment` (Multi-select)
- **Grid Layout**: 12-column responsive layout with `16 px` gutters between visual containers.

---

## 3. Seven-Page Visual Blueprints

### PAGE 1: VEYRA EXECUTIVE OVERVIEW
- **Top Row (KPI Ribbon)**: 7 Rounded KPI Cards
  1. `Total Revenue`: `$380M+` (Large 24pt Bold, orange bottom accent border)
  2. `Total Profit`: `$145M+`
  3. `Gross Margin %`: `38.2%`
  4. `Total Orders`: `500,000`
  5. `Active Customers`: `100,000`
  6. `Average Order Value (AOV)`: `$760.00`
  7. `Return Rate`: `7.8%`
- **Main Section (Middle)**:
  - **Left (60% width)**: Combined Line & Clustered Column Chart — Monthly Revenue Trend (Columns) vs. Gross Margin % (Orange Line).
  - **Right (40% width)**: Horizontal Bar Chart — Revenue Contribution by Product Category.
- **Bottom Section**:
  - **Left (50% width)**: Donut Chart — Customer Distribution by RFM Segment.
  - **Right (50% width)**: Filled Map / Treemap — Regional Revenue Breakdown (North America, Europe, APAC, LatAm).

---

### PAGE 2: SALES PERFORMANCE
- **Top KPIs**: `Monthly Revenue`, `Monthly Profit`, `YoY Revenue Growth %`, `Total Units Sold`, `Discounts Extended`.
- **Primary Visual (Full Width)**: Decomposition Tree — Revenue broken down by `Year` -> `Quarter` -> `Category` -> `Brand`.
- **Middle Visuals**:
  - **Left**: Area Chart — Revenue vs. Total Cost over time demonstrating margin spread.
  - **Right**: Matrix Table — Year-over-Year (YoY) and Month-over-Month (MoM) revenue variance with conditional formatting data bars.
- **Bottom Visual**: Scatter Plot — Order Discount % vs. Order Profit Margin to visualize margin compression from heavy promotions.

---

### PAGE 3: CUSTOMER ANALYTICS
- **Top KPIs**: `Total Customers`, `New Customers (Last 90d)`, `Repeat Customers`, `Repeat Customer Rate %`, `Average Spend per Customer (ARPU)`.
- **Visual 1**: Cohort Analysis Heatmap — Customer Retention Rate by Registration Month over subsequent order quarters.
- **Visual 2**: Clustered Bar Chart — Customer Count and Revenue by Acquisition Channel (Organic, Paid Search, Social, etc.).
- **Visual 3**: Histogram / Bin Chart — Customer Lifetime Revenue Distribution (Pareto 80/20 breakdown).
- **Visual 4**: Geographic Table — Country and City rank by Customer Density and AOV.

---

### PAGE 4: CUSTOMER SEGMENTATION
- **Top KPIs**: `Champions Count`, `Loyal Customers Count`, `Potential Loyalists Count`, `At Risk Count`, `Lost Customers Count`.
- **Visual 1 (Centerpiece)**: RFM Treemap — Segment size by Customer Count, colored by Average Monetary Spend.
- **Visual 2**: Clustered Column Chart — Average Order Value (AOV) and Order Frequency per RFM Segment.
- **Visual 3**: Scatter Plot — Customer Recency (X-axis) vs. Customer Monetary Spend (Y-axis) colored by K-Means Clusters.
- **Visual 4**: Cluster Characteristics Matrix — Comparison of the 5 K-Means cohorts across Lifespan, Average Discount, and Return Rate.

---

### PAGE 5: PRODUCT ANALYTICS
- **Top KPIs**: `Active Catalog Products`, `Top Selling Category`, `Best-Selling Product`, `Catalog Return Rate`, `Average Unit Price`.
- **Visual 1**: Ranked Table — Top 20 Best-Selling Products with columns for Brand, Category, Units Sold, Total Revenue, Gross Margin %, and Return Rate.
- **Visual 2**: Bottom 20 Underperforming Products Table — Products with lowest unit sell-through and high inventory days.
- **Visual 3**: Tornado / Diverging Bar Chart — Return Rate by Product Category (highlighting Apparel size issues vs. Grocery low returns).
- **Visual 4**: Scatter Plot — Product Unit Cost vs. Retail Unit Price with 45-degree margin benchmark line.

---

### PAGE 6: CHURN & RETENTION
- **Top KPIs**: `Active Customers`, `Medium-Risk Customers`, `High-Risk Customers`, `Total Revenue at Risk ($)`, `Average Days Since Purchase`.
- **Visual 1**: Gauge / Donut Visual — Proportion of Customer Equity at High Churn Risk.
- **Visual 2**: Bar Chart — Revenue at Risk distributed by RFM Segment (identifying high-value "Cannot Lose Them" and "At Risk" cohorts).
- **Visual 3**: Survival Curve / Retention Trend Line — % of customers repurchasing within 30, 60, 90, 180, and 365 days.
- **Visual 4**: Actionable Win-Back Table — High-Risk customers sorted by historical revenue with Days Since Last Purchase and Contact Information for CRM activation.

---

### PAGE 7: REGIONAL ANALYTICS
- **Top KPIs**: `Top Revenue Country`, `Top Margin Region`, `International Order Count`, `Fastest Growing Territory`.
- **Visual 1**: Global Bubble Map — Sized by Total Revenue, colored by Gross Margin %.
- **Visual 2**: Matrix Grid with Drill-Down Hierarchy — `Region` -> `Country` -> `State` -> `City` with expanding rows for Orders, Revenue, Margin %, and AOV.
- **Visual 3**: Bar Chart — Top 15 Metros by Order Volume (New York, London, Los Angeles, Mumbai, etc.).

---

## 4. Customer Drill-Through Page Specification
Power BI supports right-click **Drill-Through** from any visual showing a Customer onto the dedicated `Customer 360 Drill-Through Page`:
- **Header Profile**: Customer ID, Name, Email, Country, City, Registration Date, Acquisition Channel.
- **KPI Badges**:
  - `Lifetime Revenue`
  - `Total Orders Placed`
  - `Average Order Value (AOV)`
  - `RFM Score` (e.g., `555`)
  - `RFM Segment` (e.g., `Champions`)
  - `K-Means Cluster` (e.g., `High-Value VIPs`)
  - `Estimated CLV`
  - `Churn Risk` (`Low Risk`, `Medium Risk`, or `High Risk`)
  - `Last Transaction Date`
- **Transaction History Grid**: Full chronological list of all orders, products purchased, quantities, unit prices, discounts, and order statuses.
