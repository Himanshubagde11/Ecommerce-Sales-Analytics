import os

files_to_fix = [
    "powerbi/Veyra_Ecommerce_Analytics.Report/report.json",
    "python/build_powerbi_dashboard.py"
]

for rel_path in files_to_fix:
    full_path = os.path.abspath(rel_path)
    with open(full_path, "rb") as f:
        content = f.read()
    
    count = content.count(b"clusteredColumnComboLineChart")
    if count > 0:
        updated = content.replace(b"clusteredColumnComboLineChart", b"lineClusteredColumnComboChart")
        with open(full_path, "wb") as f:
            f.write(updated)
        print(f"Successfully replaced {count} occurrences in {rel_path} (saved as UTF-8 without BOM).")
    else:
        print(f"No occurrences found in {rel_path}.")

# Verification
for rel_path in files_to_fix:
    full_path = os.path.abspath(rel_path)
    with open(full_path, "rb") as f:
        data = f.read()
    assert not data.startswith(b"\xef\xbb\xbf"), f"ERROR: BOM found in {rel_path}!"
    assert b"clusteredColumnComboLineChart" not in data, f"ERROR: Old name still present in {rel_path}!"
    assert b"lineClusteredColumnComboChart" in data, f"ERROR: New name not found in {rel_path}!"
    print(f"Verified {rel_path}: No BOM, valid replacement.")
