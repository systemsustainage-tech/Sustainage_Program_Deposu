import os
import re
import json
import sys
import ast
from jinja2 import Environment, FileSystemLoader

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
LOCALES_PATH_TR = os.path.join(BASE_DIR, 'locales', 'tr.json')
LOCALES_PATH_EN = os.path.join(BASE_DIR, 'locales', 'en.json')
LOCALES_PATH_DE = os.path.join(BASE_DIR, 'locales', 'de.json')
EXCLUDE_DIRS = ['venv', '__pycache__', '.git', 'node_modules', 'static/vendor', 'frontend']

# Regex Patterns
LANG_PATTERN = re.compile(r"lang\(\s*['\"]([a-zA-Z0-9_.-]+)['\"]")
VUE_T_PATTERN = re.compile(r"\$t\(\s*['\"]([a-zA-Z0-9_.-]+)['\"]")
JS_T_PATTERN = re.compile(r"\.t\(\s*['\"]([a-zA-Z0-9_.-]+)['\"]")

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
    missing_keys_tr = set()
    errors = []
    syntax_errors = []
    route_errors = []
    
    # Setup Jinja2 Env for checking
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    try:
        if BASE_DIR not in sys.path:
            sys.path.append(BASE_DIR)
        import web_app
        flask_app = web_app.app
        valid_endpoints = set(flask_app.view_functions.keys())
        print(f"Loaded {len(valid_endpoints)} Flask endpoints for url_for checks.")
    except Exception as e:
        print(f"WARNING: Could not import web_app for endpoint checks: {e}")
        valid_endpoints = None

    # 1. Load Translation Keys
    tr_data = load_json(LOCALES_PATH_TR)
    defined_keys_tr = set(tr_data.keys())
    print(f"Loaded {len(defined_keys_tr)} translation keys from tr.json")

    # 2. Walk through files
    for root, dirs, files in os.walk(BASE_DIR):
        # Filter excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, BASE_DIR)
            
            # Read content once
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                errors.append(f"[READ ERROR] {rel_path}: {e}")
                continue

            # A. Check Python Syntax & Keys
            if ext == '.py':
                syntax_err = check_python_syntax(path)
                if syntax_err:
                    msg = f"[SYNTAX ERROR] {rel_path}: {syntax_err}"
                    errors.append(msg)
                    syntax_errors.append(msg)
                
                matches = LANG_PATTERN.findall(content)
                for key in matches:
                    used_keys.add(key)
                    if key not in defined_keys_tr:
                        missing_keys_tr.add(key)

            # B. Check HTML/Jinja & Keys
            elif ext == '.html':
                # Basic Jinja syntax check
                if 'templates' in rel_path:
                    err = check_jinja_syntax(jinja_env, os.path.relpath(path, TEMPLATES_DIR))
                    if err:
                        errors.append(f"[JINJA ERROR] {rel_path}: {err}")
                
                # Find {{ lang('key') }}
                matches = LANG_PATTERN.findall(content)
                for key in matches:
                    used_keys.add(key)
                    if key not in defined_keys_tr:
                        missing_keys_tr.add(key)

                if valid_endpoints is not None and os.path.basename(path) == "super_admin.html":
                    endpoint_matches = re.findall(r"url_for\(\s*['\"]([^'\"]+)['\"]", content)
                    for endpoint in endpoint_matches:
                        if endpoint not in valid_endpoints:
                            route_errors.append(f"[ROUTE ERROR] {rel_path}: url_for('{endpoint}') endpoint not found in Flask app.")

            # C. Check Vue/JS & Keys
            elif ext in ['.vue', '.js', '.jsx']:
                # Find $t('key') or .t('key')
                matches_vue = VUE_T_PATTERN.findall(content)
                matches_js = JS_T_PATTERN.findall(content)
                all_matches = matches_vue + matches_js
                
                for key in all_matches:
                    used_keys.add(key)
                    if key not in defined_keys_tr:
                        missing_keys_tr.add(key)
                        
    # Report Results
    print("\n--- Audit Results ---")
    if missing_keys_tr:
        print(f"Missing Turkish Keys ({len(missing_keys_tr)}):")
        for k in sorted(missing_keys_tr):
            print(f" - {k}")
    else:
        print("No missing keys found in scanned files.")

    if route_errors:
        print(f"\nRoute errors ({len(route_errors)}):")
        for err in route_errors:
            print(f" - {err}")
    else:
        print("No missing Flask endpoints detected in templates.")
    
    # Save report
    report = {
        "missing_tr": list(missing_keys_tr),
        "errors": errors,
        "syntax_errors": syntax_errors,
        "route_errors": route_errors
    }
    with open(os.path.join(BASE_DIR, 'tools', 'audit_report.json'), 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"\nAudit complete. Report saved to tools/audit_report.json")
    if syntax_errors or route_errors:
        return 1
    return 0

if __name__ == "__main__":
    exit_code = scan_files()
    sys.exit(exit_code)
