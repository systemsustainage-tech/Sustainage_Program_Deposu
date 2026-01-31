import os
import re
import glob

BASE_DIR = r"c:\SUSTAINAGESERVER"
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
WEB_APP_PATH = os.path.join(BASE_DIR, "web_app.py")

def find_missing_templates():
    print("--- Checking for Missing Templates ---")
    
    # 1. Scan python files for render_template calls
    py_files = glob.glob(os.path.join(BASE_DIR, "**", "*.py"), recursive=True)
    
    missing_templates = set()
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Regex for render_template('filename.html') or "filename.html"
            matches = re.findall(r"render_template\s*\(\s*['\"]([^'\"]+)['\"]", content)
            
            for template_name in matches:
                template_path = os.path.join(TEMPLATE_DIR, template_name)
                if not os.path.exists(template_path):
                    # Check if it's in a subdir
                    found = False
                    for root, dirs, files in os.walk(TEMPLATE_DIR):
                        if template_name in files:
                            found = True
                            break
                        # Check relative path match
                        rel_path = os.path.relpath(os.path.join(root, template_name), TEMPLATE_DIR)
                        if rel_path == template_name:
                             found = True
                             break
                    
                    if not found:
                        missing_templates.add((template_name, os.path.basename(py_file)))
                        
        except Exception as e:
            # Skip errors reading binary files etc
            pass

    if missing_templates:
        print(f"Found {len(missing_templates)} missing templates:")
        for t, f in missing_templates:
            print(f" - {t} (referenced in {f})")
    else:
        print("No missing templates found referenced in Python files.")

    return missing_templates

def check_syntax_errors():
    print("\n--- Checking for Syntax Errors in Python Files ---")
    py_files = glob.glob(os.path.join(BASE_DIR, "*.py")) + \
               glob.glob(os.path.join(BASE_DIR, "backend", "**", "*.py"), recursive=True)
               
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, py_file, 'exec')
        except SyntaxError as e:
            print(f"SYNTAX ERROR in {os.path.basename(py_file)}: {e}")
        except Exception as e:
            pass
            
    print("Syntax check complete.")

if __name__ == "__main__":
    check_syntax_errors()
    find_missing_templates()
