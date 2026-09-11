import json

with open('powerbi/Veyra_Ecommerce_Analytics.Report/report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Report ID:", data.get('id'))
print("Theme:", data.get('theme'))
sections = data.get('sections', [])
print(f"Total Sections (Pages): {len(sections)}")
total_visuals = 0
for idx, sec in enumerate(sections):
    v_count = len(sec.get('visualContainers', []))
    total_visuals += v_count
    print(f"  Page {idx+1}: '{sec.get('displayName')}' (name: {sec.get('name')}) - {v_count} visuals")

print(f"Total Visual Containers: {total_visuals}")
