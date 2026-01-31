
import re
import os
import sys

def check_decorators(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    exempt_routes = [
        '/', '/index', '/login', '/logout', '/register', 
        '/forgot-password', '/reset-password', '/health',
        '/supplier_portal/login', '/supplier_portal/register',
        '/api/public', '/static', '/uploads', '/favicon.ico'
    ]
    
    print(f"Scanning {file_path} for missing @require_company_context...")
    
    missing_count = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('@app.route') or line.startswith('@supplier_portal_bp.route'):
            route_line = line
            route_line_num = i + 1
            
            # Extract route path for checking exemption
            match = re.search(r"route\('([^']+)'", line) or re.search(r'route\("([^"]+)"', line)
            route_path = match.group(1) if match else "unknown"
            
            # Check exemptions
            is_exempt = False
            for exempt in exempt_routes:
                if route_path == exempt or route_path.startswith(exempt):
                    is_exempt = True
                    break
            
            if "reset_password" in route_path:
                is_exempt = True
            
            if route_path.startswith('/api/public'):
                 is_exempt = True

            if is_exempt:
                i += 1
                continue
            
            # Look ahead for decorators until def
            has_context_decorator = False
            has_super_admin = False
            
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('def '):
                    func_name = next_line.split('(')[0].replace('def ', '')
                    if not has_context_decorator and not has_super_admin:
                        print(f"Missing @require_company_context at line {route_line_num}: {route_path} ({func_name})")
                        missing_count += 1
                    break
                elif next_line.startswith('@require_company_context'):
                    has_context_decorator = True
                elif next_line.startswith('@super_admin_required'):
                    has_super_admin = True # super admin implicitly handles context usually, but we prefer explicit
                elif next_line.startswith('@'):
                    pass # other decorators
                else:
                    # comments or empty lines
                    pass
                j += 1
        
        i += 1
        
    print(f"\nTotal missing: {missing_count}")

if __name__ == "__main__":
    target = r"c:\SUSTAINAGESERVER\remote_web_app.py"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    check_decorators(target)
