import json
import os
import shutil
from datetime import datetime

# Determine paths dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Parent of tools/
REPORT_FILE = os.path.join(BASE_DIR, 'tools', 'missing_keys_report.json') # In tools/ dir
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
BACKEND_LOCALES_DIR = os.path.join(BASE_DIR, 'backend', 'locales')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {path}")

def backup_file(path):
    if os.path.exists(path):
        backup_path = f"{path}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy2(path, backup_path)
        print(f"Backed up {path} to {backup_path}")

def generate_default_value(key):
    # Heuristic: Convert "my_key_name" to "My Key Name"
    cleaned = key.replace('app.', '').replace('common.', '').replace('module_', '')
    parts = cleaned.replace('.', ' ').replace('_', ' ').split()
    title = ' '.join([p.capitalize() for p in parts])
    return title

def update_locales():
    if not os.path.exists(REPORT_FILE):
        # Fallback to current dir if not found in tools/
        if os.path.exists('missing_keys_report.json'):
             report_path = 'missing_keys_report.json'
        else:
             print(f"Report file {REPORT_FILE} not found. Run audit_translations.py first.")
             return
    else:
        report_path = REPORT_FILE

    with open(report_path, 'r', encoding='utf-8') as f:
        missing_keys = json.load(f)
    
    if not missing_keys:
        print("No missing keys to add.")
        return

    print(f"Found {len(missing_keys)} missing keys.")
    
    # Update ALL languages in locales/ and backend/locales/
    dirs_to_update = [LOCALES_DIR, BACKEND_LOCALES_DIR]
    
    for directory in dirs_to_update:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                data = load_json(file_path)
                backup_file(file_path)
                
                added_count = 0
                for key in missing_keys:
                    # Check if key exists (simple check)
                    if key not in data:
                        # For non-Turkish languages, we might want to add [MISSING] prefix or just English
                        # For now, use the same generated title as placeholder
                        data[key] = generate_default_value(key)
                        added_count += 1
                
                if added_count > 0:
                    save_json(file_path, data)
                    print(f"Added {added_count} keys to {filename}")
                else:
                    print(f"No new keys needed for {filename}")

if __name__ == "__main__":
    update_locales()
