
import re
import os

DASHBOARD_PATH = r"c:\SUSTAINAGESERVER\templates\dashboard.html"
BASE_PATH = r"c:\SUSTAINAGESERVER\templates\base.html"
REMOTE_APP_PATH = r"c:\SUSTAINAGESERVER\remote_web_app.py"

def get_routes_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return set(re.findall(r"url_for\(['\"]([^'\"]+)['\"]", content))

def get_implemented_routes():
    with open(REMOTE_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    return set(re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", content))

def main():
    dashboard_routes = get_routes_from_file(DASHBOARD_PATH)
    base_routes = get_routes_from_file(BASE_PATH)
    all_routes = dashboard_routes.union(base_routes)
    
    implemented_routes = get_implemented_routes()
    
    missing = []
    for route in all_routes:
        if route not in implemented_routes and route != 'static':
            missing.append(route)
            
    print("Missing routes found in dashboard.html and base.html but not in remote_web_app.py:")
    for m in missing:
        print(m)

if __name__ == "__main__":
    main()
