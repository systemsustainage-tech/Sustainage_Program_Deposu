import os
import re

WEB_APP_PATH = 'c:\\SUSTAINAGESERVER\\web_app.py'
TEMPLATES_DIR = 'c:\\SUSTAINAGESERVER\\templates'

def get_existing_routes(content):
    return set(re.findall(r'def\s+(\w+)_module\(\):', content))

def main():
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    existing_routes = get_existing_routes(content)
    
    new_routes = []
    
    for filename in os.listdir(TEMPLATES_DIR):
        if not filename.endswith('.html'):
            continue
            
        module_name = filename.replace('.html', '')
        
        # Skip base, login, etc.
        if module_name in ['base', 'login', 'index', 'dashboard', '404', '500', 'header', 'footer', 'sidebar']:
            continue
        
        # Check if route exists (checking module_name_module)
        if module_name in existing_routes:
            print(f"Route exists for {module_name}")
            continue
            
        # Also check if just module_name exists (e.g. def ai():)
        if f"def {module_name}():" in content:
            print(f"Function {module_name} exists")
            continue

        print(f"Adding route for {module_name}")
        
        route_code = f"""

@app.route('/{module_name}')
def {module_name}_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('{module_name}.html', title='{module_name.replace('_', ' ').title()}')
"""
        new_routes.append(route_code)

    if new_routes:
        with open(WEB_APP_PATH, 'a', encoding='utf-8') as f:
            f.write("".join(new_routes))
        print(f"Added {len(new_routes)} new routes.")
    else:
        print("No new routes needed.")

if __name__ == '__main__':
    main()
