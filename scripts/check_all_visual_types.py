import json

with open('powerbi/Veyra_Ecommerce_Analytics.Report/report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

for s_idx, sec in enumerate(report['sections']):
    print(f"\n=== Page {s_idx+1}: {sec['displayName']} ({len(sec['visualContainers'])} visuals) ===")
    for c_idx, vc in enumerate(sec['visualContainers']):
        cfg = json.loads(vc['config'])
        vt = cfg.get('singleVisual', {}).get('visualType')
        proj = cfg.get('singleVisual', {}).get('projections', {})
        proj_summary = {k: [item.get('queryRef') for item in v] for k, v in proj.items()}
        print(f"  Visual #{c_idx}: type='{vt}' | projections={proj_summary}")
