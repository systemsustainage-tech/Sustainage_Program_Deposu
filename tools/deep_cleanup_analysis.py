import os
import json
import re
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
LOCALES_PATH = os.path.join(BASE_DIR, 'locales', 'tr.json')

def get_all_files(directory, extensions=None):
    files_list = []
    if not os.path.exists(directory):
        return []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if extensions is None or file.endswith(tuple(extensions)):
                files_list.append(os.path.join(root, file))
    return files_list

def load_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

def analyze_cleanup():
    print("--- Deep Cleanup Analysis (Optimized) ---")
    
    # 1. Load all code content
    print("Loading code content...")
    code_files = get_all_files(TEMPLATES_DIR) + \
                 get_all_files(os.path.join(BASE_DIR, 'frontend', 'src'), ['.vue', '.js', '.ts']) + \
                 [os.path.join(BASE_DIR, 'web_app.py'), os.path.join(BASE_DIR, 'remote_web_app.py')]
    
    all_code_content = ""
    for f in code_files:
        all_code_content += load_file_content(f) + "\n"
        
    print(f"Loaded {len(code_files)} files, total {len(all_code_content)} chars.")

    # 2. Analyze Static Files
    print("Analyzing static files...")
    static_files = get_all_files(STATIC_DIR)
    unused_static = []
    
    # Exclude vendor directories from "unused" check to be safe?
    # Or just check everything.
    # Common assets usually referenced by name.
    
    for file_path in static_files:
        filename = os.path.basename(file_path)
        if filename not in all_code_content:
            # Check relative path
            rel_path = os.path.relpath(file_path, STATIC_DIR).replace('\\', '/')
            if rel_path not in all_code_content:
                unused_static.append(file_path)

    print(f"Found {len(unused_static)} unused static files.")

    # 3. Analyze Translation Keys
    print("Analyzing translation keys...")
    if not os.path.exists(LOCALES_PATH):
        print("tr.json not found")
        unused_keys = []
    else:
        with open(LOCALES_PATH, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        unused_keys = []
        for key in translations.keys():
            # Check if key is present in code
            # Simple substring check is fast but might have false positives (rare for unique keys)
            if key not in all_code_content:
                unused_keys.append(key)
    
    print(f"Found {len(unused_keys)} unused translation keys.")

    # Save report
    report = {
        "unused_static": [os.path.relpath(f, BASE_DIR) for f in unused_static],
        "unused_keys": unused_keys
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cleanup_report.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    analyze_cleanup()
