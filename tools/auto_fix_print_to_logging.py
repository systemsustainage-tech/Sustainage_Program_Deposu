import os
import re
import logging

# Configure logging for the script itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_print_statements(root_dir):
    """
    Recursively scans python files in the given directory and replaces
    print() statements with logging calls.
    Also ensures 'import logging' is present.
    """
    
    # Patterns to match print statements
    # Pattern 1: print(f"...") or print("...")
    # Pattern 2: print(var)
    # We want to be careful not to replace prints in tools that might be CLI output, 
    # but the goal is to reduce debt in core modules.
    
    # Exclude directories
    exclude_dirs = ['.git', '.vscode', '__pycache__', 'venv', 'env', 'archive', 'node_modules', 'dist', 'build', 'logs', 'data', 'exports', 'reports', 'uploads', 'assets', 'resimler']
    
    count_files_fixed = 0
    count_replacements = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if not file.endswith('.py'):
                continue
            
            # Skip this script itself
            if file == 'auto_fix_print_to_logging.py':
                continue

                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    logging.warning(f"Skipping file due to encoding error: {file_path} - {e}")
                    continue
            
            original_content = content
            has_print = False
            
            # Check if file has print statements
            if re.search(r'^\s*print\(', content, re.MULTILINE):
                has_print = True
            
            if not has_print:
                continue
                
            # Check for logging import and config
            has_logging_import = re.search(r'^\s*import\s+logging', content, re.MULTILINE) is not None
            has_basic_config = re.search(r'logging\.basicConfig', content) is not None
            
            lines = content.splitlines()
            new_lines = []
            file_modified = False
            
            for line in lines:
                # Skip comments
                if line.strip().startswith('#'):
                    new_lines.append(line)
                    continue
                
                # Regex to match print(...) handling optional comments
                # Capture indent, content inside parens, and potential trailing comment
                match = re.match(r'^(\s*)print\((.*)\)(\s*(?:#.*)?)$', line)
                
                if match:
                    indent = match.group(1)
                    args = match.group(2)
                    trailing = match.group(3) if match.group(3) else ""
                    
                    # Determine log level
                    log_level = "info"
                    if "error" in args.lower() or "hata" in args.lower() or "exception" in args.lower() or "fail" in args.lower():
                        log_level = "error"
                    elif "warning" in args.lower() or "uyarı" in args.lower():
                        log_level = "warning"
                    elif "debug" in args.lower():
                        log_level = "debug"
                        
                    # Construct new line
                    # If args looks like it has multiple arguments (comma), wrap in tuple string conversion to avoid losing data in logging
                    # But be careful about commas inside strings or function calls. 
                    # This is a simple heuristic.
                    # Better approach: just use it. If it's print(a,b), logging.info(a,b) might hide b if a is string.
                    # We will wrap it in f"{...}" if it looks like multiple args? No, too risky.
                    # We will just replace print with logging.info and append trailing comment
                    
                    new_line = f"{indent}logging.{log_level}({args}){trailing}"
                    new_lines.append(new_line)
                    file_modified = True
                    count_replacements += 1
                else:
                    new_lines.append(line)
            
            if file_modified:
                # Add import logging if missing
                insert_idx = 0
                if not has_logging_import:
                    for i, line in enumerate(new_lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_idx = i
                            break
                        if line.strip() == '' and i > 0 and (new_lines[i-1].startswith('"""') or new_lines[i-1].startswith("'''")):
                            insert_idx = i + 1
                    
                    if insert_idx == 0:
                        if len(new_lines) > 0 and (new_lines[0].startswith('#!') or new_lines[0].startswith('# -*')):
                             insert_idx = 1
                             if len(new_lines) > 1 and new_lines[1].startswith('# -*'):
                                 insert_idx = 2
                    
                    new_lines.insert(insert_idx, "import logging")
                    
                # Add basicConfig if missing and it looks like a script (has main block or is in tools/root)
                # We assume files in tools/ or root are scripts
                is_script_location = os.path.dirname(file_path) == root_dir or os.path.dirname(file_path) == os.path.join(root_dir, 'tools')
                
                if not has_basic_config and is_script_location:
                     # Find a good place to insert basicConfig
                     # After imports
                     # Re-calculate insert_idx after potential import addition
                     last_import_idx = 0
                     for i, line in enumerate(new_lines):
                         if line.startswith('import ') or line.startswith('from '):
                             last_import_idx = i
                     
                     config_line = "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')"
                     new_lines.insert(last_import_idx + 1, "")
                     new_lines.insert(last_import_idx + 2, config_line)

                # Write back to file
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines) + '\n')
                    logging.info(f"Fixed prints in: {file_path}")
                    count_files_fixed += 1
                except Exception as e:
                    logging.error(f"Failed to write file {file_path}: {e}")

    logging.info(f"Total files fixed: {count_files_fixed}")
    logging.info(f"Total print statements replaced: {count_replacements}")

if __name__ == "__main__":
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fix_print_statements(root_path)
