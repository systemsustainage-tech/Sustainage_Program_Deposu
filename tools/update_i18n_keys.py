import json
import os

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)

def update_keys():
    tr_path = r'C:\SUSTAINAGESERVER\locales\tr.json'
    en_path = r'C:\SUSTAINAGESERVER\locales\en.json'

    tr_data = load_json(tr_path)
    en_data = load_json(en_path)

    # New keys to ensure exist
    new_keys_tr = {
        "waste_type_placeholder": "Örn: Plastik, Kağıt, Metal",
        "social_type_employee": "Çalışan",
        "social_type_ohs": "İSG",
        "social_type_training": "Eğitim",
        "gov_board": "Yönetim Kurulu",
        "gov_committee": "Komite",
        "gov_ethics": "Etik",
        "industrial": "Endüstriyel",
        "domestic": "Evsel"
    }

    new_keys_en = {
        "waste_type_placeholder": "Ex: Plastic, Paper, Metal",
        "social_type_employee": "Employee",
        "social_type_ohs": "OHS",
        "social_type_training": "Training",
        "gov_board": "Board of Directors",
        "gov_committee": "Committee",
        "gov_ethics": "Ethics",
        "industrial": "Industrial",
        "domestic": "Domestic"
    }

    # Update TR
    for k, v in new_keys_tr.items():
        if k not in tr_data:
            print(f"Adding to tr.json: {k}")
            tr_data[k] = v
        # Optional: overwrite if you want to enforce the value
        # tr_data[k] = v 

    # Update EN with specific translations
    for k, v in new_keys_en.items():
        if k not in en_data:
            print(f"Adding to en.json: {k}")
            en_data[k] = v

    # Sync EN with TR (fill missing keys)
    for k, v in tr_data.items():
        if k not in en_data:
            print(f"Syncing missing key to en.json: {k}")
            # Use English specific map if available, else Capitalized key or same value?
            # Ideally we want English. Since we can't translate automatically here easily without a lib,
            # we will use the key title case or a placeholder.
            # But to be safe and usable, let's just use the key replaced with spaces and title cased.
            english_val = k.replace('_', ' ').title()
            en_data[k] = english_val

    save_json(tr_path, tr_data)
    save_json(en_path, en_data)
    print("Update complete.")

if __name__ == "__main__":
    update_keys()
