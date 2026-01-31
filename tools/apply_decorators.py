import os
import re

FILE_PATH = r"c:\SUSTAINAGESERVER\web_app.py"

EXCLUDE_PATTERNS = [
    r"def login\(",
    r"def logout\(",
    r"def index\(",
    r"def register\(",
    r"def forgot_password\(",
    r"def reset_password\(",
    r"def verify_code\(",
    r"def verify_2fa\(",
    r"def set_language\(",
    r"def health\(",
    r"def public_survey\(",
    r"def stakeholder_portal\(",
    r"def require_company_context\(", # The decorator itself
    r"def admin_required\(",
    r"def super_admin_required\(",
    r"def _init_managers\(",
    r"def get_db\(",
    r"def ensure_.*\(",
    r"def _get_.*\(",
    r"def enforce_session_timeout\(",
    # Super admin routes might be exempt or handled separately
    # r"def super_admin_.*\(", 
    # But wait, user wants isolation everywhere.
]

INCLUDE_DECORATOR = "@require_company_context"

def apply_decorators():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if it's a route definition
        if stripped.startswith("def "):
            func_name_match = re.search(r"def\s+([a-zA-Z0-9_]+)\(", stripped)
            if func_name_match:
                func_name = func_name_match.group(1)
                
                # Check exclusions
                excluded = False
                for pattern in EXCLUDE_PATTERNS:
                    if re.search(pattern, stripped):
                        excluded = True
                        break
                
                # Special exclusions
                if "super_admin" in func_name:
                    excluded = True # Usually has super_admin_required
                
                if not excluded:
                    # Look backwards for decorators
                    j = i - 1
                    decorators = []
                    while j >= 0:
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@"):
                            decorators.append(prev_line)
                            j -= 1
                        else:
                            break
                    
                    # Check if it has @app.route (it must be a route)
                    has_route = any("@app.route" in d for d in decorators)
                    has_context = any("require_company_context" in d for d in decorators)
                    
                    if has_route and not has_context:
                        # Insert decorator
                        # Find the position to insert (after @app.route or other decorators)
                        # We prefer inserting just before 'def' to be safe, or after @app.route
                        # Let's insert immediately before 'def'
                        print(f"Adding decorator to {func_name}")
                        new_lines.append(f"{INCLUDE_DECORATOR}\n")
        
        new_lines.append(line)
        i += 1
        
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    apply_decorators()
