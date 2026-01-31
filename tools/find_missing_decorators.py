import re
import os

FILES = [
    r"c:\SUSTAINAGESERVER\web_app.py",
    r"c:\SUSTAINAGESERVER\remote_web_app.py"
]

def scan_routes(file_path):
    print(f"\n--- Scanning {os.path.basename(file_path)} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    
    # Simple state machine
    current_route = None
    decorators = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('@app.route'):
            # If we were tracking a route and hit another route without seeing a def, reset (shouldn't happen in valid code usually)
            current_route = line
            decorators = []
            continue
            
        if line.startswith('@'):
            decorators.append(line)
            continue
            
        if line.startswith('def '):
            if current_route:
                func_name = line.split('(')[0].replace('def ', '')
                
                # Check isolation
                has_context = any('require_company_context' in d for d in decorators)
                has_admin = any('admin_required' in d for d in decorators) or any('super_admin_required' in d for d in decorators)
                is_login = 'login' in func_name or 'logout' in func_name or 'register' in func_name
                is_public = 'public' in func_name or 'health' in func_name or 'index' in func_name or 'static' in func_name or 'forgot_password' in func_name or 'reset_password' in func_name or 'verify_2fa' in func_name or 'set_language' in func_name
                
                # Skip known public/auth routes
                if is_login or is_public:
                    current_route = None
                    decorators = []
                    continue

                if not has_context:
                    # If it has admin_required, it might be okay for super_admin, but for regular admin it needs context.
                    # However, to be safe/strict, most should have context unless they are purely system-wide super-admin tools.
                    
                    # Special check for super_admin
                    is_super_only = any('super_admin_required' in d for d in decorators)
                    
                    if is_super_only:
                        print(f"[SUPER_ADMIN_ONLY] {func_name} (Line {i+1})")
                    else:
                        print(f"[MISSING_CONTEXT] {func_name} (Line {i+1}) - Decorators: {decorators}")
                
            current_route = None
            decorators = []

if __name__ == "__main__":
    for f in FILES:
        if os.path.exists(f):
            scan_routes(f)
        else:
            print(f"File not found: {f}")
