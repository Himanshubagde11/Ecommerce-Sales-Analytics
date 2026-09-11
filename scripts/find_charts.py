with open(r'C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.Client.Windows.dll', 'rb') as f:
    data = f.read()

text = data.decode('utf-16le', errors='ignore')

import re
matches = set(re.findall(r'\b[a-zA-Z0-9]{3,40}Chart\b', text))
print(f"Found {len(matches)} matches:")
for m in sorted(matches):
    print(" ", m)
