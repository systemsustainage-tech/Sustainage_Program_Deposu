
import json
import os
import re
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'src')
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def find_vue_keys():
    vue_files = glob.glob(os.path.join(FRONTEND_DIR, '**', '*.vue'), recursive=True)
    keys = set()
    
    # Regex for $t('key') or $t("key") or t('key')
    pattern = re.compile(r"\$t\(['\"]([^'\"]+)['\"]\)")
    
    for file_path in vue_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)
            for match in matches:
                keys.add(match)
                
    return keys

def check_keys():
    vue_keys = find_vue_keys()
    print(f"Found {len(vue_keys)} unique keys in Vue files.")
    
    langs = ['tr', 'en', 'de']
    missing = {lang: [] for lang in langs}
    
    for lang in langs:
        data = load_json(os.path.join(LOCALES_DIR, f"{lang}.json"))
        for key in vue_keys:
            if key not in data:
                missing[lang].append(key)
                
    for lang, keys in missing.items():
        print(f"Missing in {lang}: {len(keys)}")
        if keys:
            print(f"  Keys: {', '.join(keys)}")
            
    # Also check for hardcoded text in Vue files (simple heuristic)
    # Look for text between tags that is not {{}} and has letters
    print("\nPotential hardcoded text:")
    for file_path in glob.glob(os.path.join(FRONTEND_DIR, '**', '*.vue'), recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Very basic check: >Text<
                # Exclude lines with only symbols/numbers/whitespace
                matches = re.findall(r'>([^<]+)<', line)
                for match in matches:
                    text = match.strip()
                    if text and not text.startswith('{{') and re.search(r'[a-zA-Z]', text):
                        # Filter out common false positives if needed
                        print(f"  {os.path.basename(file_path)}:{i+1}: {text}")

if __name__ == "__main__":
    check_keys()
