import json
import os
import sys

def update_translations():
    """
    Updates en.json and de.json using the professional translations 
    defined in translation_dictionary.json.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locales_dir = os.path.join(base_dir, "backend", "locales")
    dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translation_dictionary.json")
    
    # Load translation dictionary
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            translation_dict = json.load(f)
        print(f"Loaded translation dictionary from {dict_path}")
    except Exception as e:
        print(f"Error loading translation dictionary: {e}")
        sys.exit(1)

    # Process each language
    for lang in ['en', 'de']:
        file_path = os.path.join(locales_dir, f"{lang}.json")
        
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping.")
            continue
            
        try:
            # Read existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Update with new translations
            updates_count = 0
            if lang in translation_dict:
                for key, value in translation_dict[lang].items():
                    # Update if key exists (to replace lazy translation) 
                    # OR if we want to enforce this key's presence
                    if key in current_data:
                        if current_data[key] != value:
                            current_data[key] = value
                            updates_count += 1
                    else:
                        # Optionally add new keys if they don't exist
                        current_data[key] = value
                        updates_count += 1
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)
                
            print(f"Updated {lang}.json with {updates_count} changes.")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    update_translations()
