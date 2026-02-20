import os
import sys

def check_unused_modules():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modules_dir = os.path.join(project_root, 'backend', 'modules')
    webapp_path = os.path.join(project_root, 'remote_web_app.py')
    
    if not os.path.exists(modules_dir):
        print("Modules directory not found")
        return

    # Get list of module folders (excluding __pycache__)
    modules = [d for d in os.listdir(modules_dir) 
               if os.path.isdir(os.path.join(modules_dir, d)) and not d.startswith('__')]
    
    # Read web_app content
    with open(webapp_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().lower()
        
    print(f"Scanning {len(modules)} modules against remote_web_app.py...")
    
    unused = []
    for mod in modules:
        # Check if module name is in content (simple string match)
        # or if there's an import like "from modules.{mod}"
        if mod not in content and f"modules.{mod}" not in content:
            unused.append(mod)
            
    if unused:
        print(f"⚠️ Potentially unused modules ({len(unused)}):")
        for mod in unused:
            print(f"  - {mod}")
    else:
        print("✅ All modules seem to be referenced.")

if __name__ == "__main__":
    check_unused_modules()
