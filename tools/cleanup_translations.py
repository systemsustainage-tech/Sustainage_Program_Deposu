import json
import os
import re
import glob

# Configuration
PROJECT_ROOT = r"c:\SUSTAINAGESERVER"
LOCALES_DIR = os.path.join(PROJECT_ROOT, "locales")
TR_JSON_PATH = os.path.join(LOCALES_DIR, "tr.json")

# Keys that are dynamically generated or special and should NOT be deleted
WHITELIST = {
    "module_environmental", "module_social_governance", "module_frameworks",
    "module_carbon", "module_energy", "module_waste", "module_water", "module_biodiversity",
    "module_social_impact", "module_corporate_governance", "module_supply_chain", "module_economic_value",
    "module_esg_score", "module_cbam",
    "status_active", "status_passive",
    "btn_add_data", "btn_back", "btn_save", "btn_cancel",
    "yes", "no", "ok", "cancel",
    "dashboard_welcome", "dashboard_role", "system_online",
    "users_title", "companies_title", "reports_title",
    "active_surveys", "total_responses"
}

def find_used_keys():
    used_keys = set()
    
    # 1. Scan HTML templates for {{ lang('KEY') }} or {{ lang('KEY', ...) }}
    # and {{ _('KEY') }}
    template_pattern = re.compile(r"""(?:lang|_)\s*\(\s*['"]([^'"]+)['"]""")
    
    for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "templates")):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = template_pattern.findall(content)
                        used_keys.update(matches)
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    # 2. Scan Python files for lang('KEY') or _('KEY') or get_text('KEY')
    # This is a heuristic and might miss some dynamic keys
    py_pattern = re.compile(r"""(?:lang|_|get_text|gettext)\s*\(\s*['"]([^'"]+)['"]""")
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = py_pattern.findall(content)
                        used_keys.update(matches)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    
    return used_keys

def main():
    if not os.path.exists(TR_JSON_PATH):
        print(f"Error: {TR_JSON_PATH} not found.")
        return

    print("Scanning for used keys...")
    used_keys = find_used_keys()
    print(f"Found {len(used_keys)} used keys.")

    try:
        with open(TR_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading tr.json: {e}")
        return

    original_count = len(data)
    keys_to_delete = []

    for key in data.keys():
        if key not in used_keys and key not in WHITELIST:
            # Simple heuristic check: if key starts with "module_" or "btn_" it might be dynamic
            # But we want to clean, so let's be strict but allow whitelist
            keys_to_delete.append(key)

    print(f"Total keys in tr.json: {original_count}")
    print(f"Candidates for deletion: {len(keys_to_delete)}")

    # Delete keys
    for key in keys_to_delete:
        del data[key]

    # Add missing keys if they don't exist
    missing_keys = {
        "companies_title": "Şirketler",
        "reports_title": "Raporlar"
    }
    
    added_count = 0
    for key, value in missing_keys.items():
        if key not in data:
            data[key] = value
            added_count += 1
            print(f"Added missing key: {key}")

    # Write back
    with open(TR_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)

    print(f"Cleanup complete. Deleted {len(keys_to_delete)} keys. Added {added_count} keys.")
    print(f"New key count: {len(data)}")

if __name__ == "__main__":
    main()
