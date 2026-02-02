import os
import re

BASE_DIR = r'c:\SUSTAINAGESERVER'
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
WEB_APP_PATH = os.path.join(BASE_DIR, 'web_app.py')
REMOTE_WEB_APP_PATH = os.path.join(BASE_DIR, 'remote_web_app.py')

def get_all_templates():
    templates = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                # Get relative path from templates dir
                rel_path = os.path.relpath(os.path.join(root, file), TEMPLATES_DIR)
                templates.append(rel_path.replace('\\', '/'))
    return templates

def get_used_templates():
    used_templates = set()
    
    # Check web_app.py and remote_web_app.py
    for file_path in [WEB_APP_PATH, REMOTE_WEB_APP_PATH]:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find render_template('...') calls
            matches = re.findall(r"render_template\s*\(\s*['\"]([^'\"]+)['\"]", content)
            used_templates.update(matches)
            
            # Also check for extends and includes in other templates
            # This is recursive, but let's do a first pass on python files
    
    # Now check inside templates for includes/extends
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # extends "..."
                    matches_extends = re.findall(r"extends\s+['\"]([^'\"]+)['\"]", content)
                    used_templates.update(matches_extends)
                    
                    # include "..."
                    matches_include = re.findall(r"include\s+['\"]([^'\"]+)['\"]", content)
                    used_templates.update(matches_include)
                    
    return used_templates

def main():
    all_templates = set(get_all_templates())
    used_templates = get_used_templates()
    
    unused = all_templates - used_templates
    
    print(f"Total Templates: {len(all_templates)}")
    print(f"Used Templates: {len(used_templates)}")
    print(f"Unused Templates: {len(unused)}")
    print("-" * 50)
    
    for t in sorted(unused):
        print(f"UNUSED: {t}")

if __name__ == "__main__":
    main()
