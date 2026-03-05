import json
import os
import glob
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_LOCALES_DIR = os.path.join(BASE_DIR, 'frontend', 'src', 'locales')
ROOT_LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def audit_frontend():
    print(f"Auditing Frontend Locales: {FRONTEND_LOCALES_DIR}")
    langs = ['tr', 'en', 'de']
    
    root_data = {lang: load_json(os.path.join(ROOT_LOCALES_DIR, f"{lang}.json")) for lang in langs}
    frontend_data = {lang: load_json(os.path.join(FRONTEND_LOCALES_DIR, f"{lang}.json")) for lang in langs}
    
    # 1. Check for missing keys in frontend compared to root (optional, maybe frontend needs subset)
    # 2. Check for missing keys in root compared to frontend (important, root should be master)
    # 3. Check for consistency across frontend languages
    
    all_frontend_keys = set()
    for lang in langs:
        all_frontend_keys.update(frontend_data[lang].keys())
        
    print(f"Total frontend keys: {len(all_frontend_keys)}")
    
    # Sync Frontend -> Root (Add missing keys to root)
    for key in all_frontend_keys:
        for lang in langs:
            if key not in root_data[lang]:
                val = frontend_data[lang].get(key, key)
                root_data[lang][key] = val
                print(f"Adding key '{key}' to root/{lang}.json")

    # Sync Root -> Frontend (Update frontend with latest root values)
    # We want frontend to have all keys available in root? Maybe not all, but let's assume we want consistency.
    # For now, let's just make sure frontend files have all keys that are currently in frontend files (cross-lang).
    
    for key in all_frontend_keys:
        for lang in langs:
            if key not in frontend_data[lang]:
                # Try to get from root, else use key
                val = root_data[lang].get(key, key)
                frontend_data[lang][key] = val
                print(f"Adding key '{key}' to frontend/{lang}.json")

    # Save updates
    for lang in langs:
        save_json(os.path.join(ROOT_LOCALES_DIR, f"{lang}.json"), root_data[lang])
        save_json(os.path.join(FRONTEND_LOCALES_DIR, f"{lang}.json"), frontend_data[lang])
        
    print("Frontend audit and sync complete.")

if __name__ == "__main__":
    audit_frontend()
