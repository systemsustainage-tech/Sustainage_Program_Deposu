import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_PATH_TR = os.path.join(BASE_DIR, 'locales', 'tr.json')
MISSING_KEYS_PATH = os.path.join(BASE_DIR, 'tools', 'missing_keys_report.json')

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

tr_data = load_json(LOCALES_PATH_TR)
missing_keys = load_json(MISSING_KEYS_PATH)

print(f"Total missing keys: {len(missing_keys)}")
print("-" * 30)

for key in missing_keys:
    tr_val = tr_data.get(key, "NO_TR_VALUE")
    # Sadece ilk 50 karakteri göster
    print(f"{key}: {tr_val}")
