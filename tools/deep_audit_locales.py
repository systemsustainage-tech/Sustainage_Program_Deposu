
import json
import os
import glob
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'src')

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def check_consistency():
    langs = ['tr', 'en', 'de']
    data = {lang: load_json(os.path.join(LOCALES_DIR, f"{lang}.json")) for lang in langs}
    
    all_keys = set()
    for lang in langs:
        all_keys.update(data[lang].keys())
        
    print(f"Total unique keys: {len(all_keys)}")
    
    missing = {lang: [] for lang in langs}
    empty = {lang: [] for lang in langs}
    same_as_key = {lang: [] for lang in langs} # Potential placeholders

    for key in all_keys:
        for lang in langs:
            if key not in data[lang]:
                missing[lang].append(key)
            else:
                val = data[lang][key]
                if not val:
                    empty[lang].append(key)
                elif val == key:
                    same_as_key[lang].append(key)

    for lang in langs:
        print(f"\n--- {lang.upper()} Analysis ---")
        print(f"Missing keys: {len(missing[lang])}")
        if missing[lang]:
            print(f"Sample: {missing[lang][:5]}")
        print(f"Empty values: {len(empty[lang])}")
        if empty[lang]:
            print(f"Sample: {empty[lang][:5]}")
        print(f"Values same as key (potential untranslated): {len(same_as_key[lang])}")
        if same_as_key[lang]:
             print(f"Sample: {same_as_key[lang][:10]}")

    return all_keys

def find_hardcoded_text():
    print("\n--- Scanning for Hardcoded Text in Vue Files ---")
    vue_files = glob.glob(os.path.join(FRONTEND_DIR, '**', '*.vue'), recursive=True)
    
    # Heuristics for hardcoded text:
    # 1. Text content inside tags: <div>Text</div>
    # 2. Text in attributes like placeholder="Text", title="Text", alt="Text"
    # We ignore text that looks like {{ variable }} or pure numbers/symbols
    
    hardcoded_warnings = []
    
    # Regex to find text between tags >TEXT<
    # Exclude: empty, whitespace, {{...}}, &nbsp;, only symbols/numbers
    text_pattern = re.compile(r'>([^<]+)<')
    
    # Attributes to check
    attr_pattern = re.compile(r'(placeholder|title|alt|label)\s*=\s*["\']([^"\']+)["\']')
    
    for file_path in vue_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check text content
            matches = text_pattern.findall(line)
            for text in matches:
                text = text.strip()
                if not text: continue
                if text.startswith('{{') or text.startswith('&') or text.startswith('v-'): continue
                # Skip if it's just numbers or symbols
                if not re.search(r'[a-zA-Z]', text): continue
                # Skip if it looks like code
                if any(c in text for c in ['=', '(', ')', '{', '}', ';']): continue
                
                hardcoded_warnings.append(f"{filename}:{i+1} Text content: '{text}'")

            # Check attributes
            matches = attr_pattern.findall(line)
            for attr, val in matches:
                val = val.strip()
                if not val: continue
                if val.startswith('{{') or val.startswith('v-') or val.startswith(':'): continue
                if not re.search(r'[a-zA-Z]', val): continue
                 # Skip if it looks like a variable or code
                if '$t' in val: continue
                
                hardcoded_warnings.append(f"{filename}:{i+1} Attribute {attr}: '{val}'")

    print(f"Found {len(hardcoded_warnings)} potential hardcoded strings.")
    for w in hardcoded_warnings[:20]: # Show first 20
        print(w)
    
    if len(hardcoded_warnings) > 20:
        print(f"... and {len(hardcoded_warnings) - 20} more.")

if __name__ == "__main__":
    check_consistency()
    find_hardcoded_text()
