import os
import re
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
TR_JSON_PATH = os.path.join(LOCALES_DIR, 'tr.json')
REPORT_FILE = os.path.join(BASE_DIR, 'tools', 'missing_keys_report.json')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def scan_files():
    keys_found = set()
    default_values = {}
    
    # Extensions to scan
    extensions = ['.html', '.py', '.js']
    
    # Walk through the project
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip some dirs
        if 'venv' in dirs: dirs.remove('venv')
        if '.git' in dirs: dirs.remove('.git')
        if 'node_modules' in dirs: dirs.remove('node_modules')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Regex for lang('key') or lang('key', 'default')
                        # Matches: {{ lang('key') }} or lang('key') in python
                        matches = re.findall(r"lang\s*\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", content)
                        
                        for key, default in matches:
                            keys_found.add(key)
                            if default:
                                default_values[key] = default
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    return keys_found, default_values

def audit(ci_mode=False):
    print("Scanning for translation keys...")
    keys_found, default_values = scan_files()
    print(f"Found {len(keys_found)} unique keys in code.")
    
    tr_data = load_json(TR_JSON_PATH)
    existing_keys = set(tr_data.keys())
    
    missing_keys = keys_found - existing_keys
    
    if missing_keys:
        print(f"ERROR: Found {len(missing_keys)} missing keys in tr.json!")
        missing_list = sorted(list(missing_keys))
        
        # Write report
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(missing_list, f, indent=4)
        print(f"Report written to {REPORT_FILE}")
        
        if ci_mode:
            exit(1)
    else:
        print("SUCCESS: All keys are present in tr.json.")
        # Clear report if exists
        if os.path.exists(REPORT_FILE):
            os.remove(REPORT_FILE)
        if ci_mode:
            exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ci', action='store_true', help='Run in CI mode (exit 1 on error)')
    args = parser.parse_args()
    
    audit(args.ci)
