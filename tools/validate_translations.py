import os
import re
import json
import glob

TEMPLATE_DIR = "templates"
MODULE_TEMPLATES_DIR = "backend/modules/*/templates"
TR_JSON_PATH = "locales/tr.json"

def load_translations():
    try:
        with open(TR_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {TR_JSON_PATH}: {e}")
        return {}

def scan_templates():
    translations = load_translations()
    missing_keys = set()
    
    # Find all html files
    files = glob.glob(os.path.join(TEMPLATE_DIR, "**/*.html"), recursive=True)
    # Also module templates? Usually they are in backend/modules/<mod>/templates
    # But current structure might be different. Let's stick to templates/ for now as main UI is there.
    
    # Check if backend modules have templates
    module_files = glob.glob("backend/modules/**/templates/*.html", recursive=True)
    files.extend(module_files)
    
    print(f"Scanning {len(files)} files...")
    
    # Regex for _('key') anywhere in the text
    # This captures the key inside the quotes
    regex_var = re.compile(r"_\(['\"](.+?)['\"]")
    
    missing_dict = {}

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find all matches
                matches = regex_var.findall(content)
                
                for key in matches:
                    if key not in translations:
                        if key not in missing_dict:
                            # Try to guess a default from context if possible, or just leave empty
                            # For now, just empty
                            missing_dict[key] = ""
                            print(f"MISSING: {key} in {file_path}")
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return missing_dict

if __name__ == "__main__":
    missing = scan_templates()
    if missing:
        print(f"\nFound {len(missing)} missing translation keys.")
        
        # Save to a file for easy merging
        with open("missing_keys.json", "w", encoding="utf-8") as f:
            json.dump(missing, f, indent=4, ensure_ascii=False)
        print("Saved missing keys to missing_keys.json")
    else:
        print("\nAll translation keys found in tr.json!")
