import json

with open("powerbi/Veyra_Ecommerce_Analytics.Report/report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

for s_idx, section in enumerate(report.get("sections", [])):
    title = section.get("displayName")
    print(f"\n--- Section {s_idx + 1}: {title} ---")
    for vc_idx, vc in enumerate(section.get("visualContainers", [])):
        config = json.loads(vc.get("config", "{}"))
        sv = config.get("singleVisual", {})
        vtype = sv.get("visualType")
        projs = list(sv.get("projections", {}).keys())
        header = sv.get("objects", {}).get("general", [{}])[0].get("properties", {}).get("title", {}).get("expr", {}).get("Literal", {}).get("Value", "")
        print(f"  Visual {vc_idx}: {vtype} | Projections: {projs} | Title: {header}")
