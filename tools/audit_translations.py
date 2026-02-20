import os
import re
import json
import logging
from typing import Set, Dict, List

# Configuration
PROJECT_ROOT = r"c:\SUSTAINAGESERVER"
LOCALES_DIR = os.path.join(PROJECT_ROOT, "locales")
TR_JSON_PATH = os.path.join(LOCALES_DIR, "tr.json")
IGNORE_DIRS = {".git", "__pycache__", "venv", "node_modules", "dist", ".trae", ".vscode"}
IGNORE_EXTS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf", ".eot"}

# Regex Patterns
PATTERNS = {
    "python": [
        r"(?:lang|gettext|_)\s*\(\s*['\"]([^'\"]+)['\"]",  # lang('key')
        r"(?:lang|gettext|_)\s*\(\s*['\"]([^'\"]+)['\"]"   # gettext('key')
    ],
    "html": [
        r"\{\{\s*lang\s*\(\s*['\"]([^'\"]+)['\"]",         # {{ lang('key') }}
        r"\{\{\s*['\"]([^'\"]+)['\"]\s*\|\s*translate",     # {{ 'key' | translate }}
        r"\$t\s*\(\s*['\"]([^'\"]+)['\"]"                   # $t('key') (in script tags)
    ],
    "js": [
        r"\$t\s*\(\s*['\"]([^'\"]+)['\"]",                  # $t('key')
        r"lang\s*\(\s*['\"]([^'\"]+)['\"]"                  # lang('key')
    ],
    "vue": [
        r"\$t\s*\(\s*['\"]([^'\"]+)['\"]",                  # $t('key')
        r"\{\{\s*\$t\s*\(\s*['\"]([^'\"]+)['\"]"            # {{ $t('key') }}
    ]
}

def load_translations(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        print(f"Error: Translation file not found at {path}")
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def scan_files(root_dir: str) -> Set[str]:
    found_keys = set()
    
    for root, dirs, files in os.walk(root_dir):
        # Ignore directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in IGNORE_EXTS:
                continue
                
            file_path = os.path.join(root, file)
            file_type = None
            
            if ext == ".py":
                file_type = "python"
            elif ext in [".html", ".htm", ".j2"]:
                file_type = "html"
            elif ext in [".js", ".ts"]:
                file_type = "js"
            elif ext == ".vue":
                file_type = "vue"
            
            if not file_type:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern in PATTERNS.get(file_type, []):
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if match and not match.startswith("{"): # Ignore variable interpolation
                                found_keys.add(match)
            except Exception as e:
                # print(f"Error reading {file_path}: {e}")
                pass
                
    return found_keys

def audit_translations():
    print("Starting Translation Audit...")
    print(f"Scanning project root: {PROJECT_ROOT}")
    
    # 1. Load existing translations
    existing_translations = load_translations(TR_JSON_PATH)
    existing_keys = set(existing_translations.keys())
    print(f"Loaded {len(existing_keys)} keys from tr.json")
    
    # 2. Scan code for keys
    code_keys = scan_files(PROJECT_ROOT)
    print(f"Found {len(code_keys)} translation keys in code")
    
    # 3. Analyze
    missing_in_json = code_keys - existing_keys
    unused_in_json = existing_keys - code_keys
    
    # 4. Report
    print("\n" + "="*50)
    print("MISSING KEYS (Found in code, missing in tr.json)")
    print("="*50)
    if missing_in_json:
        for key in sorted(missing_in_json):
            print(f"[MISSING] {key}")
            
        # Log to file
        with open("missing_keys_report.txt", "w", encoding="utf-8") as f:
            for key in sorted(missing_in_json):
                f.write(f"{key}\n")
        
        # Save as JSON for add_missing_keys.py
        with open("missing_keys_report.json", "w", encoding="utf-8") as f:
            json.dump(list(sorted(missing_in_json)), f, ensure_ascii=False, indent=4)
            
        print(f"\nReport saved to missing_keys_report.txt and missing_keys_report.json")
    else:
        print("None! All keys in code are present in tr.json.")
        
    print("\n" + "="*50)
    print("UNUSED KEYS (Found in tr.json, missing in code)")
    print("(Note: Some keys might be constructed dynamically or used in backend only)")
    print("="*50)
    # Filter out likely dynamic keys (ending in _ or generic)
    likely_dynamic = {k for k in unused_in_json if k.endswith("_") or "error" in k or "msg" in k}
    truly_unused = unused_in_json - likely_dynamic
    
    if truly_unused:
        print(f"Found {len(truly_unused)} potentially unused keys.")
        # Only show first 10
        for i, key in enumerate(sorted(truly_unused)):
            if i < 10:
                print(f"[UNUSED?] {key}")
        if len(truly_unused) > 10:
            print(f"... and {len(truly_unused) - 10} more.")
    else:
        print("None found.")

if __name__ == "__main__":
    audit_translations()
