import os
import re

WEB_APP_PATH = r"c:\SUSTAINAGESERVER\web_app.py"

DECORATOR_CODE = """
def require_company_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        # Enforce Company Context
        company_id = session.get('company_id')
        if not company_id:
            # STRICT MODE: No fallback to 1.
            # If no company context, force logout or error.
            session.clear()
            flash('Oturum süreniz doldu veya geçerli bir şirket bulunamadı.', 'warning')
            return redirect(url_for('login'))
            
        g.company_id = company_id
        return f(*args, **kwargs)
    return decorated_function
"""

def main():
    if not os.path.exists(WEB_APP_PATH):
        print(f"File not found: {WEB_APP_PATH}")
        return

    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add 'g' to Flask imports
    if 'from flask import' in content and ', g' not in content:
        content = content.replace('from flask import Flask,', 'from flask import Flask, g,')
    
    # 2. Add decorator definition if missing
    if 'def require_company_context(f):' not in content:
        # Insert after imports (e.g., after 'from core.audit_manager import AuditManager')
        # Or finding a good spot. Let's look for "app = Flask(__name__)"
        insert_marker = "app = Flask(__name__)"
        if insert_marker in content:
            parts = content.split(insert_marker)
            content = parts[0] + DECORATOR_CODE + "\n" + insert_marker + parts[1]
        else:
            print("Could not find insertion point for decorator.")
            return

    # 3. Replace session.get('company_id', 1) and add decorator
    # This is tricky with regex because we need to find the function definition enclosing the line.
    # We will use a simpler approach: 
    # Iterate over lines, track current function, if function uses session.get('company_id', 1),
    # mark it for decoration and replacement.
    
    lines = content.split('\n')
    new_lines = []
    
    current_func_start_index = -1
    current_func_name = None
    func_has_decorator = False
    
    # We need to buffer function lines to modify them
    
    # Actually, simpler:
    # 1. Replace all `session.get('company_id', 1)` with `g.company_id`
    # 2. Identify functions that NOW contain `g.company_id` but DON'T have `@require_company_context`.
    # 3. Add the decorator to those functions.
    
    # Step 3.1: Replace variable usage
    content = content.replace("session.get('company_id', 1)", "g.company_id")
    
    # Step 3.2: Re-split to process lines for decorators
    lines = content.split('\n')
    processed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for function definition
        if line.strip().startswith('def '):
            func_def_index = i
            func_indent = len(line) - len(line.lstrip())
            
            # Check if it has the decorator
            has_decorator = False
            if i > 0 and lines[i-1].strip() == '@require_company_context':
                has_decorator = True
            
            # Scan function body to see if it uses g.company_id
            uses_company_id = False
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if not next_line.strip(): # Skip empty lines
                    j += 1
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= func_indent:
                    break # End of function
                
                if 'g.company_id' in next_line:
                    uses_company_id = True
                j += 1
            
            # If uses company_id and no decorator, add it
            if uses_company_id and not has_decorator:
                # Add decorator before the function
                # We need to respect existing decorators (like @app.route)
                # Usually @require_company_context goes AFTER @app.route but BEFORE def
                
                # Look backwards for @app.route
                k = i - 1
                decorators = []
                while k >= 0:
                    prev_line = lines[k]
                    if prev_line.strip().startswith('@'):
                        decorators.insert(0, prev_line) # Store to keep order? No, we just need to insert ours.
                        # Actually, we should insert it right before 'def' if there are other decorators?
                        # Flask decorators order matters. @app.route should be outer.
                        # So @require_company_context should be inner (closer to def).
                        k -= 1
                    else:
                        break
                
                # We will insert it immediately before 'def'
                processed_lines.append(f"{' ' * func_indent}@require_company_context")
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
        
        i += 1

    final_content = '\n'.join(processed_lines)
    
    with open(WEB_APP_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("Refactoring complete.")

if __name__ == "__main__":
    main()
