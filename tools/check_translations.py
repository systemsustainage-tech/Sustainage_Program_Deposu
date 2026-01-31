
import os
import re
import json

BASE_DIR = os.getcwd()
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
LOCALE_FILE = os.path.join(BASE_DIR, 'locales', 'tr.json')
BACKEND_LOCALE_FILE = os.path.join(BASE_DIR, 'backend', 'config', 'translations_tr.json')

def load_translations():
    keys = set()
    if os.path.exists(LOCALE_FILE):
        with open(LOCALE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            keys.update(data.keys())
    
    if os.path.exists(BACKEND_LOCALE_FILE):
        with open(BACKEND_LOCALE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            keys.update(data.keys())
    return keys

def scan_templates():
    missing_keys = set()
    used_keys = set()
    
    pattern = re.compile(r"_\(['\"](.*?)['\"]\)")
    pattern_with_default = re.compile(r"_\(['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\)")
    
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Match _('key')
                    matches = pattern.findall(content)
                    for match in matches:
                        if ',' not in match: # Avoid double counting if regex overlaps
                            used_keys.add(match)
                            
                    # Match _('key', 'default')
                    matches_default = pattern_with_default.findall(content)
                    for key, default in matches_default:
                        used_keys.add(key)
    
    return used_keys

def main():
    defined_keys = load_translations()
    used_keys = scan_templates()
    
    missing = used_keys - defined_keys
    
    # Filter out keys that look like jinja variables or are empty
    missing = {k for k in missing if not k.startswith('{{') and k.strip()}
    
    print(f"Total used keys: {len(used_keys)}")
    print(f"Total defined keys: {len(defined_keys)}")
    print(f"Missing keys: {len(missing)}")
    
    if missing:
        print("\n--- Missing Keys (JSON Snippet) ---")
        print("{")
        sorted_keys = sorted(list(missing))
        for i, key in enumerate(sorted_keys):
            # Try to guess a default value (capitalize and replace _ with space)
            default_val = key.replace('_', ' ').title()
            comma = "," if i < len(sorted_keys) - 1 else ""
            print(f'    "{key}": "{default_val}"{comma}')
        print("}")

if __name__ == "__main__":
    main()
