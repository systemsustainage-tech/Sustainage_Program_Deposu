
import os
import re
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TEMPLATES_DIR = 'templates'
WEB_APP_PATH = 'web_app.py'

def get_templates():
    templates = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                # Get relative path from templates dir
                rel_path = os.path.relpath(os.path.join(root, file), TEMPLATES_DIR)
                # Normalize separators
                rel_path = rel_path.replace('\\', '/')
                templates.append(rel_path)
    return templates

def get_routes_and_rendered_templates():
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all routes
    routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', content)
    
    # Find all rendered templates
    # render_template('foo.html', ...)
    rendered = re.findall(r'render_template\([\'"]([^\'"]+)[\'"]', content)
    
    return set(routes), set(rendered)

def main():
    templates = set(get_templates())
    routes, rendered_templates = get_routes_and_rendered_templates()
    
    print(f"Total Templates: {len(templates)}")
    print(f"Total Routes: {len(routes)}")
    print(f"Rendered Templates in Code: {len(rendered_templates)}")
    
    # Find templates that are NOT rendered in web_app.py
    # Ignore partials (starting with includes/ or _)
    orphaned_templates = []
    for t in templates:
        if t.startswith('includes/') or t.startswith('errors/') or t.startswith('legal/') or 'email' in t:
            continue
        if t not in rendered_templates:
            orphaned_templates.append(t)
            
    print("\n--- Potentially Missing Routes (Templates not rendered) ---")
    for t in sorted(orphaned_templates):
        print(f"Missing Route for: {t}")

    # Special check for known missing ones
    print("\n--- Checking specific missing routes ---")
    specific_checks = ['stakeholder', 'biodiversity', 'innovation', 'quality', 'digital_security']
    for s in specific_checks:
        found = False
        for r in routes:
            if s in r:
                found = True
                break
        if not found:
            print(f"CONFIRMED MISSING: Route for '{s}'")

if __name__ == '__main__':
    main()
