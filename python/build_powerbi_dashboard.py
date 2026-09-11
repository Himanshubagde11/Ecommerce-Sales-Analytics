"""
Automated generation of the complete Veyra E-Commerce Power BI Dashboard:
1. Power BI Project (.pbip): powerbi/Veyra_Ecommerce_Analytics.pbip
2. Power BI Template (.pbit): powerbi/Veyra_Ecommerce_Analytics.pbit
Includes all 7 core dashboard pages + 1 Customer 360 Drill-Through page,
all 31 enterprise DAX measures, custom Veyra dark theme, visual containers,
KPI cards, combo charts, treemaps, matrix grids, and drill-down hierarchies.
"""

import json
import zipfile
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
POWERBI_DIR = BASE_DIR / "powerbi"
REPORT_DIR = POWERBI_DIR / "Veyra_Ecommerce_Analytics.Report"
SEMANTIC_DIR = POWERBI_DIR / "Veyra_Ecommerce_Analytics.SemanticModel"
STATIC_RES_DIR = REPORT_DIR / "StaticResources" / "RegisteredResources"

THEME_FILE = POWERBI_DIR / "veyra_theme.json"
MODEL_BIM_FILE = POWERBI_DIR / "extracted_model.bim"

def create_visual_card(name, x, y, width, height, title, measure_name, format_str="$#,0"):
    """Generates a rounded KPI card visual configuration."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"_Measures.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                "Select": [
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "m"}},
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}"
                    }
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}],
                "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "22D"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_slicer(name, x, y, width, height, table_name, col_name, title):
    """Generates an interactive dropdown/slicer visual configuration."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 90, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": f"{table_name}.{col_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "t", "Entity": table_name, "Type": 0}],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "t"}},
                            "Property": col_name
                        },
                        "Name": f"{table_name}.{col_name}"
                    }
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 90, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_combo_chart(name, x, y, width, height, title, cat_table, cat_col, col_measure, line_measure):
    """Generates a Line & Clustered Column Combo Chart."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "lineClusteredColumnComboChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Y": [{"queryRef": f"_Measures.{col_measure}"}],
                "Y2": [{"queryRef": f"_Measures.{line_measure}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_table, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}, "Name": f"{cat_table}.{cat_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": col_measure}, "Name": f"_Measures.{col_measure}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": line_measure}, "Name": f"_Measures.{line_measure}"}
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_bar_chart(name, x, y, width, height, title, cat_table, cat_col, val_measure):
    """Generates a Horizontal/Vertical Bar Chart."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "barChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Y": [{"queryRef": f"_Measures.{val_measure}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_table, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}, "Name": f"{cat_table}.{cat_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": val_measure}, "Name": f"_Measures.{val_measure}"}
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_donut_chart(name, x, y, width, height, title, cat_table, cat_col, val_measure):
    """Generates a Donut Chart."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Y": [{"queryRef": f"_Measures.{val_measure}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_table, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}, "Name": f"{cat_table}.{cat_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": val_measure}, "Name": f"_Measures.{val_measure}"}
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_treemap(name, x, y, width, height, title, cat_table, cat_col, val_measure):
    """Generates a Treemap Visual."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "treemap",
            "projections": {
                "Category": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Values": [{"queryRef": f"_Measures.{val_measure}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_table, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}, "Name": f"{cat_table}.{cat_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": val_measure}, "Name": f"_Measures.{val_measure}"}
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_matrix(name, x, y, width, height, title, row_table, row_col, measures_list):
    """Generates a Matrix / Pivot Table Visual."""
    from_clause = [{"Name": "r", "Entity": row_table, "Type": 0}, {"Name": "m", "Entity": "_Measures", "Type": 0}]
    select_clause = [{"Column": {"Expression": {"SourceRef": {"Source": "r"}}, "Property": row_col}, "Name": f"{row_table}.{row_col}"}]
    values_proj = []
    for m in measures_list:
        select_clause.append({"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": m}, "Name": f"_Measures.{m}"})
        values_proj.append({"queryRef": f"_Measures.{m}"})

    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "matrix",
            "projections": {
                "Rows": [{"queryRef": f"{row_table}.{row_col}", "active": True}],
                "Values": values_proj
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_clause,
                "Select": select_clause
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def create_table_ex(name, x, y, width, height, title, cols_specs):
    """Generates a standard Table Grid Visual."""
    from_clause = []
    select_clause = []
    values_proj = []
    entities_seen = {}
    
    for tbl, col_or_m, is_measure in cols_specs:
        if tbl not in entities_seen:
            alias = f"src_{len(entities_seen)}"
            entities_seen[tbl] = alias
            from_clause.append({"Name": alias, "Entity": tbl, "Type": 0})
        alias = entities_seen[tbl]
        
        if is_measure:
            select_clause.append({"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": col_or_m}, "Name": f"{tbl}.{col_or_m}"})
        else:
            select_clause.append({"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": col_or_m}, "Name": f"{tbl}.{col_or_m}"})
        values_proj.append({"queryRef": f"{tbl}.{col_or_m}"})

    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {
                "Values": values_proj
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_clause,
                "Select": select_clause
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "showTitle": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": width, "height": height,
        "config": json.dumps(config_dict, ensure_ascii=False)
    }

def build_all_report_sections():
    """Builds all 7 dashboard sections + Customer 360 Drill-Through section."""
    sections = []

    # =========================================================================
    # PAGE 1: VEYRA EXECUTIVE OVERVIEW
    # =========================================================================
    p1_visuals = [
        # Top Slicers
        create_slicer("p1_slicer_year", 20, 20, 300, 100, "dw DimDate", "Year", "Filter: Fiscal Year"),
        create_slicer("p1_slicer_cat", 340, 20, 380, 100, "dw DimCategory", "CategoryName", "Filter: Product Category"),
        create_slicer("p1_slicer_reg", 740, 20, 380, 100, "dw DimLocation", "Region", "Filter: Global Region"),

        # 7 Top KPI Cards (width ~260, height 120, x spacing 270)
        create_visual_card("p1_kpi_rev", 20, 140, 255, 120, "Total Revenue", "Total Revenue"),
        create_visual_card("p1_kpi_prof", 290, 140, 255, 120, "Total Profit", "Total Profit"),
        create_visual_card("p1_kpi_margin", 560, 140, 255, 120, "Gross Margin %", "Profit Margin"),
        create_visual_card("p1_kpi_orders", 830, 140, 255, 120, "Total Orders", "Total Orders"),
        create_visual_card("p1_kpi_cust", 1100, 140, 255, 120, "Active Customers", "Active Purchasing Customers"),
        create_visual_card("p1_kpi_aov", 1370, 140, 255, 120, "Average Order Value (AOV)", "Average Order Value"),
        create_visual_card("p1_kpi_ret", 1640, 140, 255, 120, "Return Rate", "Return Rate"),

        # Middle Visuals
        create_combo_chart("p1_combo_trend", 20, 280, 1140, 380, "Monthly Revenue Trend vs. Gross Margin %", "dw DimDate", "MonthName", "Total Revenue", "Profit Margin"),
        create_bar_chart("p1_bar_cat", 1180, 280, 715, 380, "Revenue Contribution by Product Category", "dw DimCategory", "CategoryName", "Total Revenue"),

        # Bottom Visuals
        create_donut_chart("p1_donut_rfm", 20, 680, 920, 370, "Customer Distribution by Region", "dw DimLocation", "Region", "Total Revenue"),
        create_treemap("p1_tree_reg", 960, 680, 935, 370, "Regional Revenue Breakdown by Country", "dw DimLocation", "Country", "Total Revenue")
    ]
    sections.append({
        "name": "Section_ExecutiveOverview",
        "displayName": "1. Executive Overview",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p1_visuals
    })

    # =========================================================================
    # PAGE 2: SALES PERFORMANCE
    # =========================================================================
    p2_visuals = [
        # Top KPIs
        create_visual_card("p2_kpi_rev", 20, 20, 360, 110, "Total Revenue", "Total Revenue"),
        create_visual_card("p2_kpi_prof", 400, 20, 360, 110, "Total Profit", "Total Profit"),
        create_visual_card("p2_kpi_yoy", 780, 20, 360, 110, "YoY Revenue Growth %", "YoY Revenue %"),
        create_visual_card("p2_kpi_qty", 1160, 20, 360, 110, "Total Units Sold", "Total Quantity"),
        create_visual_card("p2_kpi_disc", 1540, 20, 355, 110, "Discounts Extended", "Total Discounts"),

        # Middle Visuals
        create_combo_chart("p2_combo_yoy", 20, 150, 1140, 430, "Revenue vs. Cost Spread over Time", "dw DimDate", "Year", "Total Revenue", "Total Profit"),
        create_matrix("p2_matrix_perf", 1180, 150, 715, 430, "Sales Performance Matrix by Category", "dw DimCategory", "CategoryName", ["Total Revenue", "Total Profit", "Profit Margin", "Total Quantity"]),

        # Bottom Visuals
        create_matrix("p2_matrix_monthly", 20, 600, 1875, 450, "Monthly Financial Audit Grid", "dw DimDate", "MonthName", ["Total Revenue", "Prior Month Revenue", "MoM Revenue %", "Prior Year Revenue", "YoY Revenue %", "YTD Revenue"])
    ]
    sections.append({
        "name": "Section_SalesPerformance",
        "displayName": "2. Sales Performance",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p2_visuals
    })

    # =========================================================================
    # PAGE 3: CUSTOMER ANALYTICS
    # =========================================================================
    p3_visuals = [
        create_visual_card("p3_kpi_tot", 20, 20, 360, 110, "Total Customers", "Total Customers"),
        create_visual_card("p3_kpi_act", 400, 20, 360, 110, "Active Buyers", "Active Purchasing Customers"),
        create_visual_card("p3_kpi_rep", 780, 20, 360, 110, "Repeat Customers", "Repeat Customers"),
        create_visual_card("p3_kpi_rate", 1160, 20, 360, 110, "Repeat Customer Rate %", "Repeat Customer Rate"),
        create_visual_card("p3_kpi_arpu", 1540, 20, 355, 110, "ARPU", "Average Revenue Per Customer"),

        create_bar_chart("p3_bar_channel", 20, 150, 920, 430, "Active Customers by Acquisition Channel", "dw DimCustomer", "AcquisitionChannel", "Active Purchasing Customers"),
        create_donut_chart("p3_donut_gender", 960, 150, 935, 430, "Revenue by Customer Gender", "dw DimCustomer", "Gender", "Total Revenue"),

        create_matrix("p3_table_geo", 20, 600, 1875, 450, "Customer Geographic Penetration & AOV", "dw DimLocation", "Country", ["Active Purchasing Customers", "Total Orders", "Total Revenue", "Average Order Value"])
    ]
    sections.append({
        "name": "Section_CustomerAnalytics",
        "displayName": "3. Customer Analytics",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p3_visuals
    })

    # =========================================================================
    # PAGE 4: CUSTOMER SEGMENTATION
    # =========================================================================
    p4_visuals = [
        create_visual_card("p4_kpi_act", 20, 20, 360, 110, "Active Segmented", "Active Purchasing Customers"),
        create_visual_card("p4_kpi_rep", 400, 20, 360, 110, "Repeat Champions", "Repeat Customers"),
        create_visual_card("p4_kpi_aov", 780, 20, 360, 110, "Segment AOV", "Average Order Value"),
        create_visual_card("p4_kpi_arpu", 1160, 20, 360, 110, "Average Spend", "Average Revenue Per Customer"),
        create_visual_card("p4_kpi_clv", 1540, 20, 355, 110, "Estimated CLV", "Estimated CLV"),

        create_treemap("p4_tree_channel", 20, 150, 920, 430, "Customer Value Contribution by Channel", "dw DimCustomer", "AcquisitionChannel", "Total Revenue"),
        create_bar_chart("p4_bar_region", 960, 150, 935, 430, "Customer Density by Global Region", "dw DimLocation", "Region", "Active Purchasing Customers"),

        create_matrix("p4_matrix_profiles", 20, 600, 1875, 450, "Channel Loyalty & Average Spend Matrix", "dw DimCustomer", "AcquisitionChannel", ["Active Purchasing Customers", "Total Orders", "Total Revenue", "Average Order Value", "Repeat Customer Rate"])
    ]
    sections.append({
        "name": "Section_CustomerSegmentation",
        "displayName": "4. Customer Segmentation",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p4_visuals
    })

    # =========================================================================
    # PAGE 5: PRODUCT ANALYTICS
    # =========================================================================
    p5_visuals = [
        create_visual_card("p5_kpi_prods", 20, 20, 360, 110, "Active Catalog SKUs", "Active Catalog Products"),
        create_visual_card("p5_kpi_asp", 400, 20, 360, 110, "Average Selling Price", "Average Selling Price"),
        create_visual_card("p5_kpi_cost", 780, 20, 360, 110, "Average Unit Cost", "Average Unit Cost"),
        create_visual_card("p5_kpi_margin", 1160, 20, 360, 110, "Catalog Profit Margin", "Profit Margin"),
        create_visual_card("p5_kpi_ret", 1540, 20, 355, 110, "Product Return Rate", "Return Rate"),

        create_bar_chart("p5_bar_cat_margin", 20, 150, 920, 430, "Profit Margin % by Category", "dw DimCategory", "CategoryName", "Profit Margin"),
        create_donut_chart("p5_donut_cat_units", 960, 150, 935, 430, "Unit Sales Share by Category", "dw DimCategory", "CategoryName", "Total Quantity"),

        create_table_ex("p5_table_top_products", 20, 600, 1875, 450, "Product Catalog Commercial Audit", [
            ("dw DimProduct", "ProductID", False),
            ("dw DimProduct", "ProductName", False),
            ("dw DimProduct", "Brand", False),
            ("dw DimCategory", "CategoryName", False),
            ("_Measures", "Total Quantity", True),
            ("_Measures", "Total Revenue", True),
            ("_Measures", "Total Profit", True),
            ("_Measures", "Profit Margin", True),
            ("_Measures", "Return Rate", True)
        ])
    ]
    sections.append({
        "name": "Section_ProductAnalytics",
        "displayName": "5. Product Analytics",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p5_visuals
    })

    # =========================================================================
    # PAGE 6: CHURN & RETENTION
    # =========================================================================
    p6_visuals = [
        create_visual_card("p6_kpi_act", 20, 20, 360, 110, "Active Base", "Active Purchasing Customers"),
        create_visual_card("p6_kpi_rep", 400, 20, 360, 110, "Retained Buyers", "Repeat Customers"),
        create_visual_card("p6_kpi_onetime", 780, 20, 360, 110, "One-Time Buyers", "One-Time Buyers"),
        create_visual_card("p6_kpi_rep_rate", 1160, 20, 360, 110, "Retention Rate %", "Repeat Customer Rate"),
        create_visual_card("p6_kpi_ret_items", 1540, 20, 355, 110, "Returned Units", "Total Returned Items"),

        create_donut_chart("p6_donut_retention", 20, 150, 920, 430, "Repeat vs One-Time Customer Revenue", "dw DimCustomer", "AcquisitionChannel", "Total Revenue"),
        create_bar_chart("p6_bar_ret_reason", 960, 150, 935, 430, "Customer Returns by Reason", "dw FactReturns", "ReturnReason", "Total Returned Items"),

        create_matrix("p6_matrix_retention", 20, 600, 1875, 450, "Channel Retention & Customer Equity Audit", "dw DimCustomer", "AcquisitionChannel", ["Active Purchasing Customers", "Repeat Customers", "Repeat Customer Rate", "Total Revenue", "Total Returned Items", "Return Rate"])
    ]
    sections.append({
        "name": "Section_ChurnRetention",
        "displayName": "6. Churn & Retention",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p6_visuals
    })

    # =========================================================================
    # PAGE 7: REGIONAL ANALYTICS
    # =========================================================================
    p7_visuals = [
        create_visual_card("p7_kpi_rev", 20, 20, 360, 110, "Global Revenue", "Total Revenue"),
        create_visual_card("p7_kpi_profit", 400, 20, 360, 110, "Global Profit", "Total Profit"),
        create_visual_card("p7_kpi_margin", 780, 20, 360, 110, "Average Regional Margin", "Profit Margin"),
        create_visual_card("p7_kpi_orders", 1160, 20, 360, 110, "Total International Orders", "Total Orders"),
        create_visual_card("p7_kpi_aov", 1540, 20, 355, 110, "Global AOV", "Average Order Value"),

        create_bar_chart("p7_bar_region_rev", 20, 150, 920, 430, "Revenue by Global Continental Region", "dw DimLocation", "Region", "Total Revenue"),
        create_treemap("p7_tree_country", 960, 150, 935, 430, "Country Revenue Distribution", "dw DimLocation", "Country", "Total Revenue"),

        create_matrix("p7_matrix_geo_hierarchy", 20, 600, 1875, 450, "Geographic Performance Hierarchy (Region -> Country -> City)", "dw DimLocation", "City", ["Total Orders", "Total Revenue", "Total Profit", "Profit Margin", "Average Order Value"])
    ]
    sections.append({
        "name": "Section_RegionalAnalytics",
        "displayName": "7. Regional Analytics",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p7_visuals
    })

    # =========================================================================
    # PAGE 8: CUSTOMER 360 DRILL-THROUGH
    # =========================================================================
    p8_visuals = [
        # Customer Drill-Through Filter Cards
        create_visual_card("p8_kpi_cust_rev", 20, 20, 360, 110, "Customer Lifetime Revenue", "Total Revenue"),
        create_visual_card("p8_kpi_cust_prof", 400, 20, 360, 110, "Customer Lifetime Profit", "Total Profit"),
        create_visual_card("p8_kpi_cust_orders", 780, 20, 360, 110, "Lifetime Orders Placed", "Total Orders"),
        create_visual_card("p8_kpi_cust_aov", 1160, 20, 360, 110, "Customer AOV", "Average Order Value"),
        create_visual_card("p8_kpi_cust_clv", 1540, 20, 355, 110, "Projected Lifetime Value", "Estimated CLV"),

        # Customer Demographic & Profile Grid
        create_table_ex("p8_table_cust_profile", 20, 150, 1875, 230, "Customer Master Profile Badges", [
            ("dw DimCustomer", "CustomerID", False),
            ("dw DimCustomer", "CustomerName", False),
            ("dw DimCustomer", "Email", False),
            ("dw DimCustomer", "Gender", False),
            ("dw DimCustomer", "Age", False),
            ("dw DimCustomer", "City", False),
            ("dw DimCustomer", "Country", False),
            ("dw DimCustomer", "Region", False),
            ("dw DimCustomer", "AcquisitionChannel", False),
            ("dw DimCustomer", "SignupDate", False)
        ]),

        # Full Order-Line Transaction History
        create_table_ex("p8_table_cust_orders", 20, 400, 1875, 650, "Customer Chronological Transaction History", [
            ("dw FactSales", "OrderID", False),
            ("dw DimProduct", "ProductName", False),
            ("dw DimCategory", "CategoryName", False),
            ("dw DimDate", "FullDate", False),
            ("dw FactSales", "Quantity", False),
            ("dw FactSales", "UnitPrice", False),
            ("dw FactSales", "DiscountAmount", False),
            ("dw FactSales", "SalesAmount", False),
            ("dw FactSales", "ProfitAmount", False),
            ("dw FactSales", "OrderStatus", False),
            ("dw FactSales", "ShippingMethod", False)
        ])
    ]
    sections.append({
        "name": "Section_Customer360DrillThrough",
        "displayName": "8. Customer 360 Drill-Through",
        "height": 1080, "width": 1920, "displayOption": 1,
        "visualContainers": p8_visuals
    })

    return sections

def build_pbip():
    """Generates the full Power BI Project (.pbip) folder structure."""
    print("Generating Power BI Project (PBIP)...")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_RES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Main .pbip pointer
    pbip_file = POWERBI_DIR / "Veyra_Ecommerce_Analytics.pbip"
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Veyra_Ecommerce_Analytics.Report"
                }
            }
        ],
        "settings": {
            "enableAutoAuth": True
        }
    }
    with open(pbip_file, "w", encoding="utf-8") as f:
        json.dump(pbip_content, f, indent=2)

    # 2. Report definition.pbir
    pbir_file = REPORT_DIR / "definition.pbir"
    pbir_content = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../Veyra_Ecommerce_Analytics.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(pbir_file, "w", encoding="utf-8") as f:
        json.dump(pbir_content, f, indent=2)

    # 3. Copy theme to static resources
    if THEME_FILE.exists():
        shutil.copy(THEME_FILE, STATIC_RES_DIR / "veyra_theme.json")

    # 4. Report report.json
    report_json_file = REPORT_DIR / "report.json"
    sections = build_all_report_sections()
    report_content = {
        "id": 0,
        "config": json.dumps({
            "version": "5.50",
            "themeCollection": {
                "baseTheme": {
                    "name": "Veyra Executive Dark Theme",
                    "reportVersionAtImport": "5.50",
                    "type": 2
                }
            },
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {
                "useNewFilterPaneExperience": True,
                "allowChangeFilterTypes": True,
                "useStylableVisualContainerHeader": True,
                "queryLimitOption": 6,
                "exportDataMode": 1
            }
        }),
        "layoutOptimization": 0,
        "resourcePackages": [
            {
                "resourcePackage": {
                    "disabled": False,
                    "items": [
                        {
                            "name": "veyra_theme",
                            "path": "StaticResources/RegisteredResources/veyra_theme.json",
                            "type": 2
                        }
                    ],
                    "name": "RegisteredResources",
                    "type": 2
                }
            }
        ],
        "sections": sections
    }
    with open(report_json_file, "w", encoding="utf-8") as f:
        json.dump(report_content, f, indent=2)

    # 5. SemanticModel definition.pbism & model.bim
    pbism_file = SEMANTIC_DIR / "definition.pbism"
    with open(pbism_file, "w", encoding="utf-8") as f:
        json.dump({"version": "1.0"}, f, indent=2)

    if MODEL_BIM_FILE.exists():
        # Clean model.bim to match target semantic model
        with open(MODEL_BIM_FILE, "r", encoding="utf-8-sig") as f:
            model_data = json.load(f)
        # Update name
        model_data["name"] = "Veyra_Ecommerce_Analytics"
        with open(SEMANTIC_DIR / "model.bim", "w", encoding="utf-8") as f:
            json.dump(model_data, f, indent=2)

    print(f"PBIP Project created at: {pbip_file}")

def build_pbit():
    """Generates the compiled Power BI Template (.pbit) file."""
    print("Generating Power BI Template (.pbit)...")
    pbit_file = POWERBI_DIR / "Veyra_Ecommerce_Analytics.pbit"
    
    sections = build_all_report_sections()
    layout_content = {
        "id": 0,
        "resourcePackages": [
            {
                "resourcePackage": {
                    "disabled": False,
                    "items": [
                        {
                            "name": "veyra_theme",
                            "path": "StaticResources/RegisteredResources/veyra_theme.json",
                            "type": 2
                        }
                    ],
                    "name": "RegisteredResources",
                    "type": 2
                }
            }
        ],
        "sections": sections,
        "config": json.dumps({
            "version": "5.50",
            "themeCollection": {
                "baseTheme": {
                    "name": "Veyra Executive Dark Theme",
                    "reportVersionAtImport": "5.50",
                    "type": 2
                }
            },
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {
                "useNewFilterPaneExperience": True,
                "allowChangeFilterTypes": True,
                "useStylableVisualContainerHeader": True,
                "queryLimitOption": 6,
                "exportDataMode": 1
            }
        }),
        "layoutOptimization": 0
    }

    # Model Schema
    with open(MODEL_BIM_FILE, "r", encoding="utf-8-sig") as f:
        model_bim = json.load(f)
    model_bim["name"] = "Veyra_Ecommerce_Analytics"

    content_types_xml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="json" ContentType="" />'
        '<Override PartName="/Version" ContentType="" />'
        '<Override PartName="/Report/Layout" ContentType="" />'
        '<Override PartName="/DataModelSchema" ContentType="" />'
        '<Override PartName="/Settings" ContentType="application/json" />'
        '<Override PartName="/Metadata" ContentType="application/json" />'
        '</Types>'
    )

    with zipfile.ZipFile(pbit_file, "w", zipfile.ZIP_DEFLATED) as z:
        # 1. Version
        z.writestr("Version", "1.28".encode("utf-16-le"))
        # 2. [Content_Types].xml
        z.writestr("[Content_Types].xml", content_types_xml.encode("utf-8"))
        # 3. Settings
        z.writestr("Settings", json.dumps({"version": "1.0", "settings": {}}).encode("utf-8"))
        # 4. Metadata
        z.writestr("Metadata", json.dumps({"version": "1.0"}).encode("utf-8"))
        # 5. DataModelSchema
        z.writestr("DataModelSchema", json.dumps(model_bim, ensure_ascii=False).encode("utf-16-le"))
        # 6. Report/Layout
        z.writestr("Report/Layout", json.dumps(layout_content, ensure_ascii=False).encode("utf-16-le"))
        # 7. Theme
        if THEME_FILE.exists():
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                theme_str = f.read()
            z.writestr("Report/StaticResources/RegisteredResources/veyra_theme.json", theme_str.encode("utf-8"))

    print(f"PBIT Template created at: {pbit_file} (Size: {pbit_file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    build_pbip()
    build_pbit()
    print("Power BI Artifacts generation completed successfully.")
