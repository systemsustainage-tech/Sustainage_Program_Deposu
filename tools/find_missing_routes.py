import re
import os

TEMPLATES_DIR = 'templates'
REMOTE_APP = 'remote_web_app.py'

def get_url_endpoints(files):
    endpoints = set()
    for fname in files:
        path = os.path.join(TEMPLATES_DIR, fname)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r"url_for\('([^']+)'", content)
            endpoints.update(matches)
            matches_double = re.findall(r'url_for\("([^"]+)"', content)
            endpoints.update(matches_double)
    return endpoints

def get_defined_routes(app_file):
    routes = set()
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find @app.route('/path') -> def function_name():
        # Actually flask url_for uses the function name.
        # So we need to find "def function_name():" that are decorated with @app.route
        
        # Simple regex for def following @app.route
        # It's not perfect but good enough for 99% cases in this file
        # Pattern: @app.route(...) \n ... \n def func_name
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                # Check if previous non-empty lines had @app.route
                # Look back a few lines
                is_route = False
                for j in range(1, 5):
                    if i-j >= 0:
                        prev = lines[i-j].strip()
                        if prev.startswith('@app.route'):
                            is_route = True
                            break
                        if prev.startswith('@'): # other decorators
                            continue
                        if prev == '' or prev.startswith('#'):
                            continue
                        break # Stopped being decorators
                
                if is_route:
                    routes.add(func_name)
    return routes

def main():
    # Dashboard and Base are critical
    endpoints = get_url_endpoints(['dashboard.html', 'base.html'])
    defined = get_defined_routes(REMOTE_APP)
    
    missing = endpoints - defined
    # static is built-in
    if 'static' in missing: missing.remove('static')
    
    print(f"Found {len(endpoints)} endpoints in templates.")
    print(f"Found {len(defined)} defined routes in {REMOTE_APP}.")
    print(f"Missing {len(missing)} endpoints:")
    for m in sorted(missing):
        print(f" - {m}")

if __name__ == '__main__':
    main()
