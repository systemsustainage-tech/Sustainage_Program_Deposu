
import json
import os

DICT_PATH = 'c:/SUSTAINAGESERVER/tools/translation_dictionary.json'

new_keys = {
    "last_update": {
        "tr": "Son güncelleme",
        "en": "Last update"
    },
    "data_entry": {
        "tr": "Veri girişi",
        "en": "Data entry"
    },
    "carbon_footprint": {
        "tr": "Karbon Ayak İzi",
        "en": "Carbon Footprint"
    },
    "survey_results": {
        "tr": "Anket Sonuçları",
        "en": "Survey Results"
    },
    "active_period": {
        "tr": "Aktif Dönem",
        "en": "Active Period"
    }
}

try:
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update data
    for k, v in new_keys.items():
        if k not in data:
            data[k] = v
            print(f"Added {k}")
        else:
            # Merge if exists but missing langs
            if "tr" not in data[k] and "tr" in v:
                data[k]["tr"] = v["tr"]
            if "en" not in data[k] and "en" in v:
                data[k]["en"] = v["en"]
            print(f"Updated {k}")

    with open(DICT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Dictionary updated.")
except Exception as e:
    print(f"Error: {e}")
