import json
import os

# 1. Update report.json
report_path = "powerbi/Veyra_Ecommerce_Analytics.Report/report.json"
with open(report_path, "r", encoding="utf-8") as f:
    report = json.load(f)

treemap_count = 0
for section in report.get("sections", []):
    for vc in section.get("visualContainers", []):
        cfg = json.loads(vc.get("config", "{}"))
        sv = cfg.get("singleVisual", {})
        if sv.get("visualType") == "treemap":
            treemap_count += 1
            projs = sv.get("projections", {})
            if "Category" in projs:
                projs["Group"] = projs.pop("Category")
            
            # Ensure data labels and category labels are enabled
            objs = sv.setdefault("objects", {})
            objs["labels"] = [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
            objs["categoryLabels"] = [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
            
            vc["config"] = json.dumps(cfg)

with open(report_path, "wb") as f:
    f.write(json.dumps(report, indent=2).encode("utf-8"))

print(f"Updated {treemap_count} treemap visuals in report.json (Category -> Group, labels enabled).")

# 2. Update veyra_theme.json in both locations
theme_files = [
    "powerbi/veyra_theme.json",
    "powerbi/Veyra_Ecommerce_Analytics.Report/StaticResources/RegisteredResources/veyra_theme.json"
]

for tf in theme_files:
    with open(tf, "r", encoding="utf-8") as f:
        theme = json.load(f)
    
    vs = theme.setdefault("visualStyles", {})
    vs["treemap"] = {
        "*": {
            "labels": [
                {
                    "show": True,
                    "color": {"solid": {"color": "#FFFFFF"}},
                    "fontSize": 11,
                    "fontFamily": "Segoe UI Semibold"
                }
            ],
            "categoryLabels": [
                {
                    "show": True,
                    "color": {"solid": {"color": "#00F2FE"}},
                    "fontSize": 12,
                    "fontFamily": "Segoe UI Bold"
                }
            ]
        }
    }
    
    with open(tf, "wb") as f:
        f.write(json.dumps(theme, indent=2).encode("utf-8"))
    print(f"Updated treemap styling in {tf}.")

# 3. Update build_powerbi_dashboard.py
build_script = "python/build_powerbi_dashboard.py"
with open(build_script, "r", encoding="utf-8") as f:
    code = f.read()

old_treemap_block = '''def create_treemap(name, x, y, width, height, title, cat_table, cat_col, val_measure):
    """Generates a Treemap Visual."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "treemap",
            "projections": {
                "Category": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Values": [{"queryRef": f"_Measures.{val_measure}"}]
            },'''

new_treemap_block = '''def create_treemap(name, x, y, width, height, title, cat_table, cat_col, val_measure):
    """Generates a Treemap Visual."""
    config_dict = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": width, "height": height}}],
        "singleVisual": {
            "visualType": "treemap",
            "projections": {
                "Group": [{"queryRef": f"{cat_table}.{cat_col}", "active": True}],
                "Values": [{"queryRef": f"_Measures.{val_measure}"}]
            },'''

if old_treemap_block in code:
    code = code.replace(old_treemap_block, new_treemap_block)
    with open(build_script, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated python/build_powerbi_dashboard.py with Group projection.")

# 4. Verify no BOM
for check_f in [report_path] + theme_files:
    with open(check_f, "rb") as f:
        raw = f.read()
    assert not raw.startswith(b"\xef\xbb\xbf"), f"BOM detected in {check_f}"
print("All files strictly verified UTF-8 without BOM!")
