import os
import sys

DESKTOP_MODULES_PATH = r'c:\sdg\modules'
WEB_ROOT = r'c:\SUSTAINAGESERVER'
WEB_MODULES_PATH = os.path.join(WEB_ROOT, 'modules')
WEB_BACKEND_MODULES_PATH = os.path.join(WEB_ROOT, 'backend', 'modules')
TEMPLATES_PATH = os.path.join(WEB_ROOT, 'templates')
WEB_APP_PATH = os.path.join(WEB_ROOT, 'web_app.py')

def get_desktop_modules():
    if not os.path.exists(DESKTOP_MODULES_PATH):
        print(f"Error: {DESKTOP_MODULES_PATH} does not exist.")
        return []
    return [d for d in os.listdir(DESKTOP_MODULES_PATH) if os.path.isdir(os.path.join(DESKTOP_MODULES_PATH, d)) and not d.startswith('__')]

def check_web_module(module_name):
    status = {
        'desktop_exists': True,
        'web_module_exists': False,
        'web_backend_module_exists': False,
        'template_exists': False,
        'manager_imported': False
    }
    
    # Check web modules path
    if os.path.exists(os.path.join(WEB_MODULES_PATH, module_name)):
        status['web_module_exists'] = True
        
    # Check web backend modules path
    if os.path.exists(os.path.join(WEB_BACKEND_MODULES_PATH, module_name)):
        status['web_backend_module_exists'] = True
        
    # Check templates
    if os.path.exists(os.path.join(TEMPLATES_PATH, f'{module_name}.html')):
        status['template_exists'] = True
        
    # Check web_app.py imports (simple string check)
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        if f'modules.{module_name}' in content or f"MANAGERS['{module_name}']" in content:
            status['manager_imported'] = True
            
    return status

def generate_report():
    modules = get_desktop_modules()
    print(f"Found {len(modules)} modules in Desktop version.")
    
    print("\n| Module | Web Module | Backend Module | Template | Imported in web_app | Action Needed |")
    print("|---|---|---|---|---|---|")
    
    missing_critical = []
    
    for mod in modules:
        status = check_web_module(mod)
        action = "OK"
        if not status['web_module_exists'] and not status['web_backend_module_exists']:
            action = "MISSING BACKEND"
            missing_critical.append(mod)
        elif not status['template_exists']:
            action = "MISSING TEMPLATE"
        elif not status['manager_imported']:
            action = "NOT INTEGRATED"
            
        web_mod = "✅" if status['web_module_exists'] else "❌"
        back_mod = "✅" if status['web_backend_module_exists'] else "❌"
        tmpl = "✅" if status['template_exists'] else "❌"
        imp = "✅" if status['manager_imported'] else "❌"
        
        print(f"| {mod} | {web_mod} | {back_mod} | {tmpl} | {imp} | {action} |")

    print("\n--- Summary ---")
    print(f"Missing Backends: {', '.join(missing_critical)}")

if __name__ == "__main__":
    generate_report()
