import json

with open('powerbi/Veyra_Ecommerce_Analytics.SemanticModel/model.bim', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('CompatibilityLevel:', data.get('compatibilityLevel'))
tables = data.get('model', {}).get('tables', [])
print('Tables count:', len(tables))
for t in tables:
    print(f"  Table: {t['name']} (cols: {len(t.get('columns', []))}, measures: {len(t.get('measures', []))})")
print('Relationships count:', len(data.get('model', {}).get('relationships', [])))
