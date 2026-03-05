
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def export_missing():
    langs = ['tr', 'en', 'de']
    data = {lang: load_json(os.path.join(LOCALES_DIR, f"{lang}.json")) for lang in langs}
    
    all_keys = set()
    for lang in langs:
        all_keys.update(data[lang].keys())
        
    missing_report = {
        "tr_missing": [],
        "de_missing": []
    }

    # We use EN as the source of truth for values if available
    en_data = data['en']

    for key in all_keys:
        # Check TR
        if key not in data['tr']:
            en_val = en_data.get(key, key)
            missing_report["tr_missing"].append({"key": key, "en_value": en_val})
            
        # Check DE
        if key not in data['de']:
            en_val = en_data.get(key, key)
            missing_report["de_missing"].append({"key": key, "en_value": en_val})

    with open('missing_report.json', 'w', encoding='utf-8') as f:
        json.dump(missing_report, f, ensure_ascii=False, indent=4)
        
    print(f"Exported {len(missing_report['tr_missing'])} missing TR keys.")
    print(f"Exported {len(missing_report['de_missing'])} missing DE keys.")

if __name__ == "__main__":
    export_missing()
