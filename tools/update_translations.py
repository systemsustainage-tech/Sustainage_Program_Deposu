import json
import os
import glob

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
FRONTEND_LOCALES_DIR = os.path.join(BASE_DIR, 'frontend', 'src', 'locales')
DICT_PATH = os.path.join(TOOLS_DIR, 'translation_dictionary.json')

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
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved: {path}")
    except Exception as e:
        print(f"Error saving {path}: {e}")

def update_translations():
    print("Loading translation dictionary...")
    dictionary = load_json(DICT_PATH)
    
    if not dictionary:
        print("Dictionary is empty or could not be loaded!")
        return

    # Initialize language maps
    translations = {
        "tr": {},
        "en": {},
        "de": {}
    }

    # Load existing translations to preserve any keys not in dictionary (optional)
    for lang in translations.keys():
        file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
        translations[lang] = load_json(file_path)

    # Update with dictionary values
    for key, values in dictionary.items():
        if not isinstance(values, dict):
            continue
            
        # Handle "tr": { "key": "val" } structure
        if key in ["tr", "en", "de", "fr", "es", "it", "ja", "ko", "pt", "ru", "zh", "nl", "ar"]:
            lang = key
            if lang in translations:
                for k, v in values.items():
                    translations[lang][k] = v
            continue

        # Handle "key": { "tr": "val" } structure
        if "tr" in values:
            translations["tr"][key] = values["tr"]
        if "en" in values:
            translations["en"][key] = values["en"]
        if "de" in values:
            translations["de"][key] = values["de"]
            
    # Save files
    for lang, data in translations.items():
        # Save to backend locales
        file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
        save_json(file_path, data)
        
        # Save to frontend locales
        if os.path.exists(os.path.dirname(FRONTEND_LOCALES_DIR)):
            if not os.path.exists(FRONTEND_LOCALES_DIR):
                os.makedirs(FRONTEND_LOCALES_DIR)
            fe_path = os.path.join(FRONTEND_LOCALES_DIR, f"{lang}.json")
            save_json(fe_path, data)

    print("All translations updated successfully.")

def cleanup_mess():
    # Remove files that are named after keys (not tr.json or en.json)
    # Be careful not to delete legitimate language files if there were any others
    # But for now assuming only tr and en are valid
    print("Cleaning up incorrect locale files...")
    files = glob.glob(os.path.join(LOCALES_DIR, "*.json"))
    for f in files:
        filename = os.path.basename(f)
        if filename not in ["tr.json", "en.json", "de.json"]:
            print(f"Deleting incorrect file: {filename}")
            os.remove(f)

if __name__ == "__main__":
    if not os.path.exists(LOCALES_DIR):
        os.makedirs(LOCALES_DIR)
        
    update_translations()
    cleanup_mess()
