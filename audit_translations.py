import re
import os
import json

TEMPLATE_DIR = 'c:/SUSTAINAGESERVER/templates'
LOCALE_FILE = 'c:/SUSTAINAGESERVER/locales/tr.json'

def get_translation_keys():
    with open(LOCALE_FILE, 'r', encoding='utf-8') as f:
        return set(json.load(f).keys())

def scan_templates():
    existing_keys = get_translation_keys()
    missing_keys = set()
    
    # Regex to find {{ _('key') }} or {{ _("key") }}
    pattern = re.compile(r"_\(['\"](.*?)['\"]\)")
    
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(TEMPLATE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.findall(content)
                for match in matches:
                    if match not in existing_keys:
                        missing_keys.add(match)
                        print(f"Missing key in {filename}: {match}")

    return missing_keys

if __name__ == "__main__":
    print("Scanning for missing translation keys...")
    missing = scan_templates()
    if missing:
        print(f"\nFound {len(missing)} missing keys.")
        print(missing)
    else:
        print("\nNo missing keys found!")
