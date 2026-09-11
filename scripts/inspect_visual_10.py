import json

with open('powerbi/Veyra_Ecommerce_Analytics.Report/report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

# Page 1 visual #10
sec1 = report['sections'][0]
print("Section 1:", sec1['displayName'])
v10 = sec1['visualContainers'][10]
cfg10 = json.loads(v10['config'])
print("Visual 10 config:")
print("  visualType:", cfg10.get('singleVisual', {}).get('visualType'))
print("  projections:", json.dumps(cfg10.get('singleVisual', {}).get('projections'), indent=2))

# Also Page 2 visual #5
sec2 = report['sections'][1]
print("\nSection 2:", sec2['displayName'])
v5 = sec2['visualContainers'][5]
cfg5 = json.loads(v5['config'])
print("Visual 5 config:")
print("  visualType:", cfg5.get('singleVisual', {}).get('visualType'))
print("  projections:", json.dumps(cfg5.get('singleVisual', {}).get('projections'), indent=2))
