# Power BI Desktop Setup & Connection Guide: VEYRA Data Warehouse

This step-by-step guide explains how to connect Microsoft Power BI Desktop to the `VeyraDW` SQL Server Data Warehouse and configure the data model, DAX measures, and theme.

---

## 1. Prerequisites
- **Microsoft Power BI Desktop** (Updated release).
- **Microsoft SQL Server** (2017 or newer / Azure SQL / LocalDB) hosting `VeyraDW`.
- Completed execution of SQL scripts `01_create_database.sql` through `15_create_views.sql` with staged data loaded.

---

## 2. Connecting Power BI to SQL Server

### Step 1: Open Power BI Desktop & Get Data
1. Launch Power BI Desktop.
2. In the **Home** ribbon, click **Get Data** -> Select **SQL Server database** -> Click **Connect**.

### Step 2: Configure Server & Database Connection
1. In the SQL Server Database dialog:
   - **Server**: `localhost` (or `.\SQLEXPRESS` / your server name or IP).
   - **Database**: `VeyraDW`.
   - **Data Connectivity Mode**:
     - Select **Import** (Recommended for blazing-fast in-memory VertiPaq compression and advanced DAX time-intelligence).
     - Or select **DirectQuery** if your enterprise mandates real-time queries against the 2M+ SQL Server Columnstore index.
2. Under **Data Connectivity options**, check:
   - `Include relationship columns`.
   - `Navigate using full hierarchy`.
3. Click **OK**.

### Step 3: Authentication
- If running on local Windows, select **Windows Authentication** -> **Use current credentials**.
- If connecting to a remote SQL Server with a dedicated account, select **Database** -> enter User Name `sa` and Password -> Click **Connect**.

### Step 4: Navigator — Selecting Tables & Views
In the Navigator window, expand `VeyraDW` and check the following objects:

**Core Star Schema Tables (Recommended for full drill-through)**:
- `dw.FactSales`
- `dw.FactReturns`
- `dw.DimCustomer`
- `dw.DimProduct`
- `dw.DimCategory`
- `dw.DimDate`
- `dw.DimLocation`
- `dw.DimPayment`

**Or High-Speed Analytics Views (For lightweight dashboards)**:
- `analytics.vw_MonthlySales`
- `analytics.vw_CategoryPerformance`
- `analytics.vw_ProductPerformance`
- `analytics.vw_CustomerValue`
- `analytics.vw_RegionalPerformance`
- `analytics.vw_RFMCustomer`
- `analytics.vw_CustomerChurn`
- `analytics.vw_CLV`

Click **Load** (or **Transform Data** in Power Query to inspect column types).

---

## 3. Configuring the Data Model Relationships
1. Switch to the **Model View** (icon on the left sidebar).
2. Verify that Power BI has detected the Star Schema relationships outlined in `powerbi/data_model.md`:
   - `FactSales[CustomerKey]` -> `DimCustomer[CustomerKey]` (1:*, Single)
   - `FactSales[ProductKey]` -> `DimProduct[ProductKey]` (1:*, Single)
   - `FactSales[OrderDateKey]` -> `DimDate[DateKey]` (1:*, Single)
   - `FactSales[LocationKey]` -> `DimLocation[LocationKey]` (1:*, Single)
   - `FactSales[PaymentKey]` -> `DimPayment[PaymentKey]` (1:*, Single)
   - `FactReturns[ProductKey]` -> `DimProduct[ProductKey]` (1:*, Single)
   - `FactReturns[ReturnDateKey]` -> `DimDate[DateKey]` (1:*, Single)
3. Right-click `DimDate` -> select **Mark as Date Table** -> Select column `FullDate` -> Click **OK**.

---

## 4. Creating the Dedicated Measures Table
1. On the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. In the Fields pane, right-click `_Measures` -> click **New Measure**.
4. Copy and paste each DAX measure from [`powerbi/dax_measures.md`](file:///powerbi/dax_measures.md).
5. Delete the default empty `Column1` from `_Measures`. The table will now display with a calculator icon at the top of the Fields pane!

---

## 5. Instant Deployment: Power BI Project (.pbip) & Template (.pbit)

The complete multi-page Power BI dashboard has been programmatically generated with all 8 pages, 69 visuals, and 31 DAX measures:

### Option A: Open the Power BI Project (Recommended)
1. In Windows File Explorer, navigate to:
   `D:\Portfolio Projects\E-commers sales analytics\powerbi\`
2. Double-click **`Veyra_Ecommerce_Analytics.pbip`**.
3. Power BI Desktop will launch with all 8 pages, visual containers, charts, KPI cards, and measures automatically connected to `localhost.VeyraDW`.
4. In Power BI Desktop, click **File** -> **Save As** -> Save as **`Veyra_Ecommerce_Analytics.pbix`**.

### Option B: Open the Power BI Template (.pbit)
1. Double-click **`Veyra_Ecommerce_Analytics.pbit`** in `powerbi/`.
2. Power BI Desktop will prompt to connect and import all 8 pages and star schema tables.
3. Click **File** -> **Save As** -> Save as **`Veyra_Ecommerce_Analytics.pbix`**.

### Option C: Use Your Currently Active Power BI Desktop Session
If you already have Power BI Desktop connected to `localhost.VeyraDW`:
1. The **`_Measures`** table has been injected live into your running model with all 31 enterprise measures organized into 5 display folders.
2. **`dw DimDate`** has been marked as the official Date Table.
3. Import the theme from [`powerbi/veyra_theme.json`](file:///d:/Portfolio%20Projects/E-commers%20sales%20analytics/powerbi/veyra_theme.json) (**View** ribbon -> **Themes** -> **Browse for themes**).
4. Follow the visual blueprints in [`powerbi/dashboard_design.md`](file:///d:/Portfolio%20Projects/E-commers%20sales%20analytics/powerbi/dashboard_design.md).

