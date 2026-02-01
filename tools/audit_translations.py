import re
import os
import json
import glob
import argparse
import sys

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Parent of tools/ is root
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
LOCALE_FILE = os.path.join(PROJECT_ROOT, 'locales', 'tr.json')

def load_existing_keys():
    if not os.path.exists(LOCALE_FILE):
        print(f"Warning: Locale file not found at {LOCALE_FILE}")
        return set()
    with open(LOCALE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return flatten_keys(data)

def flatten_keys(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key, sep=sep))
        else:
            items.append(new_key)
    return set(items)

def scan_codebase():
    existing_keys = load_existing_keys()
    print(f"Loaded {len(existing_keys)} existing keys.")
    
    missing_keys = set()
    used_keys = set()

    # Regex patterns for different translation function usages
    patterns = [
        re.compile(r"_\(['\"](.*?)['\"]", re.MULTILINE),
        re.compile(r"get_text\(['\"](.*?)['\"]", re.MULTILINE),
        re.compile(r"lang\(['\"](.*?)['\"]", re.MULTILINE),
        re.compile(r"\$t\(['\"](.*?)['\"]", re.MULTILINE)
    ]

    files_to_scan = []
    # Recursive templates
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html') or file.endswith('.js'):
                files_to_scan.append(os.path.join(root, file))
    
    # Recursive backend
    for root, dirs, files in os.walk(BACKEND_DIR):
        for file in files:
            if file.endswith('.py'):
                files_to_scan.append(os.path.join(root, file))
                
    # Also root py files
    for file in glob.glob(os.path.join(PROJECT_ROOT, '*.py')):
         files_to_scan.append(file)
         
    # Frontend src files
    frontend_src = os.path.join(PROJECT_ROOT, 'frontend', 'src')
    if os.path.exists(frontend_src):
        for root, dirs, files in os.walk(frontend_src):
            for file in files:
                if file.endswith('.vue') or file.endswith('.js'):
                    files_to_scan.append(os.path.join(root, file))

    print(f"Scanning {len(files_to_scan)} files...")

    for filepath in files_to_scan:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for p in patterns:
                    matches = p.findall(content)
                    for match in matches:
                        if '{' in match or '}' in match: 
                            continue 
                        
                        used_keys.add(match)
                        
                        if match not in existing_keys:
                            missing_keys.add(match)
                            # print(f"Missing: {match} in {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    return missing_keys, used_keys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Audit translations for missing keys.')
    parser.add_argument('--ci', action='store_true', help='Exit with error code if missing keys found')
    args = parser.parse_args()

    missing, used = scan_codebase()
    print(f"\nTotal used keys: {len(used)}")
    print(f"Missing keys: {len(missing)}")
    
    if missing:
        print("\nMISSING KEYS:")
        for k in sorted(missing):
            print(f" - {k}")
        
        # Save to report file for add_missing_keys.py
        with open('missing_keys_report.json', 'w', encoding='utf-8') as f:
            json.dump(list(missing), f, indent=4)
        print("\nReport saved to missing_keys_report.json")
            
    if args.ci and missing:
        print("\n[CI] Build failed due to missing translation keys.")
        sys.exit(1)
    
    if not missing:
        print("\nAll translation keys are present. Good job!")
        sys.exit(0)
