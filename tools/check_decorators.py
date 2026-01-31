
import re
import os

def check_decorators():
    file_path = r"c:\SUSTAINAGESERVER\remote_web_app.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    exempt_routes = [
        '/', '/index', '/login', '/logout', '/register', 
        '/forgot-password', '/reset-password', '/health',
        '/supplier_portal/login', '/supplier_portal/register',
        '/api/public', '/static', '/uploads'
    ]
    
    # Also exempt reset_password related routes with tokens
    # e.g. /reset-password/<token>
    
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

            if is_exempt:
                i += 1
                continue
            
            # Look ahead for decorators until def
            has_context_decorator = False
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('def '):
                    break
                if '@require_company_context' in next_line:
                    has_context_decorator = True
                j += 1
            
            if not has_context_decorator:
                print(f"Line {route_line_num}: Missing @require_company_context -> {route_line}")
                missing_count += 1
                
        i += 1

    print(f"\nTotal missing: {missing_count}")

if __name__ == "__main__":
    check_decorators()
