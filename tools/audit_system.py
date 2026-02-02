import os
import re
import json
import sys
import ast
from jinja2 import Environment, FileSystemLoader

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
LOCALES_PATH = os.path.join(BASE_DIR, 'locales', 'tr.json')
EXCLUDE_DIRS = ['venv', '__pycache__', '.git', 'node_modules', 'static/vendor', 'frontend']

# Regex Patterns
LANG_PATTERN = re.compile(r"lang\(\s*['\"]([a-zA-Z0-9_.-]+)['\"]")
INLINE_CONFIRM_PATTERN = re.compile(r'onclick\s*=\s*["\']\s*return\s+confirm\(')
CONSOLE_LOG_PATTERN = re.compile(r'console\.log\(')
ALERT_PATTERN = re.compile(r'alert\(')

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load {path}: {e}")
        return {}

def check_python_syntax(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=path)
        return None
    except SyntaxError as e:
        return f"{e.msg} (Line {e.lineno})"
    except Exception as e:
        return str(e)

def check_jinja_syntax(env, template_name):
    try:
        with open(os.path.join(TEMPLATES_DIR, template_name), 'r', encoding='utf-8') as f:
            source = f.read()
        env.parse(source)
        return None
    except Exception as e:
        return str(e)

def scan_files():
    print(f"Scanning project rooted at {BASE_DIR}...")
    
    used_keys = set()
    errors = []
    warnings = []
    
    # Setup Jinja2 Env for checking
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # 1. Load Translation Keys
    tr_data = load_json(LOCALES_PATH)
    defined_keys = set(tr_data.keys())
    print(f"Loaded {len(defined_keys)} translation keys from tr.json")

    # 2. Walk through files
    for root, dirs, files in os.walk(BASE_DIR):
        # Filter excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, BASE_DIR)
            
            # A. Check Python Syntax
            if ext == '.py':
                syntax_err = check_python_syntax(path)
                if syntax_err:
                    errors.append(f"[SYNTAX ERROR] {rel_path}: {syntax_err}")
                
                # Also check content for keys
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = LANG_PATTERN.findall(content)
                        for key in matches:
                            used_keys.add(key)
                            if key not in defined_keys:
                                errors.append(f"[MISSING TRANS] {rel_path}: Key '{key}' not found in tr.json")
                except:
                    pass

            # B. Check HTML/Jinja
            if ext == '.html':
                # Jinja Syntax
                if root.startswith(TEMPLATES_DIR):
                    # Rel path inside templates dir
                    tmpl_name = os.path.relpath(path, TEMPLATES_DIR).replace('\\', '/')
                    # Only check if it's directly in templates or subdirs, avoid partials if they are weird
                    # But parse() handles most.
                    jinja_err = check_jinja_syntax(jinja_env, tmpl_name)
                    if jinja_err:
                        errors.append(f"[TEMPLATE ERROR] {rel_path}: {jinja_err}")

                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.splitlines()
                        
                    # Find Translation Usage
                    matches = LANG_PATTERN.findall(content)
                    for key in matches:
                        used_keys.add(key)
                        if key not in defined_keys:
                            errors.append(f"[MISSING TRANS] {rel_path}: Key '{key}' not found in tr.json")

                    # Dangerous Patterns
                    for i, line in enumerate(lines):
                        if INLINE_CONFIRM_PATTERN.search(line):
                            errors.append(f"[BAD CODE] {rel_path}:{i+1} Found inline 'onclick=return confirm(...)'. Use 'data-confirm-message' instead.")
                        if CONSOLE_LOG_PATTERN.search(line) and 'static/vendor' not in rel_path:
                             warnings.append(f"[CLEANUP] {rel_path}:{i+1} Found 'console.log()'.")
                        if ALERT_PATTERN.search(line) and 'static/vendor' not in rel_path:
                             warnings.append(f"[UX] {rel_path}:{i+1} Found 'alert()'. Prefer custom modals or toasts.")
                except Exception as e:
                    print(f"Could not read {rel_path}: {e}")

            # C. Check JS
            if ext == '.js':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.splitlines()
                    
                    for i, line in enumerate(lines):
                        if CONSOLE_LOG_PATTERN.search(line) and 'static/vendor' not in rel_path:
                             warnings.append(f"[CLEANUP] {rel_path}:{i+1} Found 'console.log()'.")
                        if ALERT_PATTERN.search(line) and 'static/vendor' not in rel_path:
                             warnings.append(f"[UX] {rel_path}:{i+1} Found 'alert()'. Prefer custom modals or toasts.")
                except:
                    pass

    # 3. Report Results
    print("\n" + "="*50)
    print("AUDIT REPORT")
    print("="*50)
    
    if errors:
        print(f"\nFound {len(errors)} CRITICAL ISSUES:")
        for err in errors:
            print(f"  [X] {err}")
    else:
        print("\n[OK] No CRITICAL ISSUES found.")

    if warnings:
        print(f"\nFound {len(warnings)} WARNINGS (Cleanup recommended):")
        for warn in warnings[:10]:
            print(f"  [!] {warn}")
        if len(warnings) > 10:
            print(f"  ...and {len(warnings)-10} more.")
    else:
        print("\n[OK] No WARNINGS found.")
        
    print(f"\nINFO: {len(defined_keys - used_keys)} keys in tr.json appear to be unused in scanned code (dynamic keys excluded).")
    
    return len(errors)

if __name__ == "__main__":
    count = scan_files()
    sys.exit(1 if count > 0 else 0)
