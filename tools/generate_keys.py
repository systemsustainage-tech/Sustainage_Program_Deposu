import os
import json
import re

def extract_keys_from_file(filepath):
    keys = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Pattern 1: lang('key') or lang("key")
    # Pattern 2: lang('key', 'Default')
    
    # We look for lang( followed by quote, capturing key, then optional comma and quote capturing default
    
    # Regex for lang('key', 'default') or lang('key')
    # Matches: lang('my.key', 'My Default') -> group 1: my.key, group 3: My Default
    # Also support _()
    pattern = re.compile(r"(?:lang|_)\(\s*['\"](.+?)['\"]\s*(,\s*['\"](.+?)['\"])?.*?\)")
    
    matches = pattern.findall(content)
    for match in matches:
        key = match[0]
        default = match[2] if match[2] else ""
        keys[key] = default
        
    return keys

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    backend_dir = os.path.join(base_dir, 'backend') # Also scan backend
    web_app_path = os.path.join(base_dir, 'web_app.py')
    
    locales_dir = os.path.join(base_dir, 'locales')
    tr_path = os.path.join(locales_dir, 'tr.json')
    
    if not os.path.exists(tr_path):
        print("tr.json not found!")
        return

    print("Scanning for translation keys...")
    found_keys = {}
    
    # Scan templates
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                file_keys = extract_keys_from_file(path)
                for k, v in file_keys.items():
                    if k not in found_keys or (not found_keys[k] and v):
                        found_keys[k] = v

    # Scan web_app.py
    if os.path.exists(web_app_path):
        file_keys = extract_keys_from_file(web_app_path)
        for k, v in file_keys.items():
            if k not in found_keys or (not found_keys[k] and v):
                found_keys[k] = v
                
    # Scan backend python files
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                file_keys = extract_keys_from_file(path)
                for k, v in file_keys.items():
                    if k not in found_keys or (not found_keys[k] and v):
                        found_keys[k] = v

    print(f"Found {len(found_keys)} unique keys.")
    
    # Load existing tr.json
    try:
        with open(tr_path, 'r', encoding='utf-8') as f:
            tr_data = json.load(f)
    except Exception as e:
        print(f"Error loading tr.json: {e}")
        tr_data = {}
        
    added_count = 0
    
    # Helper to set nested key
    def set_nested(data, key_path, value):
        parts = key_path.split('.')
        curr = data
        for i, part in enumerate(parts[:-1]):
            if part not in curr:
                curr[part] = {}
            elif not isinstance(curr[part], dict):
                # Conflict: key exists but is not a dict. 
                # e.g. "menu" is "Menu" string, but we want "menu.sub"
                # For now, print warning and skip or rename
                print(f"Warning: Key conflict for {key_path} at {part}")
                return False
            curr = curr[part]
        
        last = parts[-1]
        if last not in curr:
            curr[last] = value
            return True
        return False # Already exists

    # Helper to check nested key
    def has_nested(data, key_path):
        parts = key_path.split('.')
        curr = data
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return False
        return True

    for key, default in found_keys.items():
        if not has_nested(tr_data, key):
            val = default if default else key
            if set_nested(tr_data, key, val):
                print(f"Added: {key} = {val}")
                added_count += 1
                
    if added_count > 0:
        print(f"Saving {added_count} new keys to tr.json...")
        with open(tr_path, 'w', encoding='utf-8') as f:
            json.dump(tr_data, f, indent=4, ensure_ascii=False)
    else:
        print("No new keys found.")

if __name__ == "__main__":
    main()
