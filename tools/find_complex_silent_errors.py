import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_complex_silent_errors(root_dir):
    """
    Scans for except blocks that are effectively silent (pass or only comments).
    """
    exclude_dirs = ['.git', '.vscode', '__pycache__', 'venv', 'env', 'archive', 'node_modules', 'dist', 'build', 'logs', 'data', 'exports', 'reports', 'uploads', 'assets', 'resimler']
    
    silent_errors = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if not file.endswith('.py'):
                continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
                
            lines = content.splitlines()
            
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Check for except block
                if stripped.startswith('except') and stripped.endswith(':'):
                    indent = len(line) - len(line.lstrip())
                    
                    # Look ahead to see body
                    j = i + 1
                    body_lines = []
                    is_silent = True
                    has_pass = False
                    has_logging = False
                    has_raise = False
                    has_code = False
                    
                    while j < len(lines):
                        next_line = lines[j]
                        next_stripped = next_line.strip()
                        
                        # Skip empty lines
                        if not next_stripped:
                            j += 1
                            continue
                            
                        # Check indentation
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent <= indent:
                            break # End of block
                            
                        # Check content
                        if next_stripped == 'pass':
                            has_pass = True
                        elif next_stripped.startswith('pass '): # pass # comment
                             has_pass = True
                        elif next_stripped.startswith('#'):
                            pass # Just comment
                        elif 'logging.' in next_stripped:
                            has_logging = True
                            has_code = True
                        elif 'print(' in next_stripped:
                             # print is technically code, but we want logging
                             has_code = True 
                        elif 'raise' in next_stripped:
                            has_raise = True
                            has_code = True
                        else:
                            has_code = True
                        
                        j += 1
                    
                    # Analyze block
                    if not has_code and not has_logging and not has_raise:
                        # It has no real code, only pass or comments
                        silent_errors.append((file_path, i + 1, line))
                        
                i += 1
                
    return silent_errors

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = find_complex_silent_errors(root_dir)
    for path, line_no, content in errors:
        logging.info(f"Silent Error at {path}:{line_no} -> {content.strip()}")
    logging.info(f"Found {len(errors)} complex silent errors.")
