import json

with open('powerbi/Veyra_Ecommerce_Analytics.Report/report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

vtypes = {}
for s_idx, sec in enumerate(data.get('sections', [])):
    s_name = sec.get('displayName')
    for c_idx, c in enumerate(sec.get('visualContainers', [])):
        cfg_str = c.get('config')
        if cfg_str:
            cfg = json.loads(cfg_str)
            vt = cfg.get('singleVisual', {}).get('visualType')
            if vt not in vtypes:
                vtypes[vt] = []
            vtypes[vt].append((s_name, c_idx))

print(f"Total distinct visual types used: {len(vtypes)}")
for vt, occurrences in sorted(vtypes.items()):
    print(f"\nVisualType: '{vt}' ({len(occurrences)} occurrences)")
    for s_name, c_idx in occurrences[:3]:
        print(f"  Page: {s_name}, Visual #{c_idx}")
    if len(occurrences) > 3:
        print(f"  ... and {len(occurrences) - 3} more")
