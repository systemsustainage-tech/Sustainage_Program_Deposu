import json
import os

path = r"c:\SUSTAINAGESERVER\locales\tr.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

key = "audit_logs"
print(f"Checking '{key}' in {path}")
if key in data:
    print(f"FOUND: '{key}': '{data[key]}'")
else:
    print(f"NOT FOUND: '{key}'")

# Check for keys starting with audit_logs
print("Keys starting with 'audit_logs':")
for k in data.keys():
    if k.startswith("audit_logs"):
        print(f"  {k}")
