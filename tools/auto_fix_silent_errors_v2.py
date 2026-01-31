import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logging.error(f"Skipping {filepath} (read error): {e}")
        return

    original_content = content
    modified = False
    
    # Check if logging is imported
    has_logging = re.search(r'^\s*import\s+logging', content, re.MULTILINE) or \
                  re.search(r'^\s*from\s+logging\s+import', content, re.MULTILINE)
    
    # Helper to add import logging if needed
    def ensure_logging(c):
        nonlocal has_logging
        if not has_logging:
            # Add after the first non-comment line or at top
            lines = c.splitlines()
            insert_idx = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('#') and line.strip():
                    insert_idx = i
                    break
            lines.insert(insert_idx, "import logging")
            has_logging = True
            return "\n".join(lines)
        return c

    # Pattern 1: Bare except
    # except:\n\s+pass
    def replace_bare(match):
        indent = match.group(1)
        return f"except Exception as e:\n{indent}logging.error(f'Silent error in {os.path.basename(filepath)}: {{str(e)}}')"

    new_content = re.sub(r'except\s*:\s*\n(\s+)pass', replace_bare, content)
    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    # Pattern 2: except Exception: pass (no 'as')
    # except (Exception|ValueError|...) :\n\s+pass
    def replace_no_as(match):
        exc_type = match.group(1)
        indent = match.group(2)
        if ' as ' in exc_type:
            return match.group(0) # Skip if already has 'as'
        return f"except {exc_type} as e:\n{indent}logging.error(f'Silent error in {os.path.basename(filepath)}: {{str(e)}}')"

    new_content = re.sub(r'except\s+([a-zA-Z0-9_\.]+)\s*:\s*\n(\s+)pass', replace_no_as, content)
    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    # Pattern 3: except ... as e: pass
    def replace_with_as(match):
        exc_part = match.group(1) # e.g. "Exception as e"
        var_name = exc_part.split(' as ')[-1].strip()
        indent = match.group(2)
        return f"except {exc_part}:\n{indent}logging.error(f'Silent error in {os.path.basename(filepath)}: {{{var_name}}}')"

    new_content = re.sub(r'except\s+(.+?\s+as\s+\w+)\s*:\s*\n(\s+)pass', replace_with_as, content)
    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    # Pattern 4: Tuple exceptions without 'as'
    # except (A, B):\n\s+pass
    def replace_tuple_no_as(match):
        exc_type = match.group(1)
        indent = match.group(2)
        return f"except {exc_type} as e:\n{indent}logging.error(f'Silent error in {os.path.basename(filepath)}: {{str(e)}}')"

    new_content = re.sub(r'except\s+(\(.*?\))\s*:\s*\n(\s+)pass', replace_tuple_no_as, content)
    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    # Pattern 5: Tuple exceptions with 'as'
    # except (A, B) as e:\n\s+pass
    def replace_tuple_with_as(match):
        exc_part = match.group(1)
        var_name = exc_part.split(' as ')[-1].strip()
        indent = match.group(2)
        return f"except {exc_part}:\n{indent}logging.error(f'Silent error in {os.path.basename(filepath)}: {{str({var_name})}}')"

    new_content = re.sub(r'except\s+(\(.*?\)\s+as\s+\w+)\s*:\s*\n(\s+)pass', replace_tuple_with_as, content)
    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    # Pattern 6: Multiline with comments (except:\n # comment\n pass)
    # except (Exception|ValueError|...) :\n\s*(#.*)?\n\s*pass
    def replace_multiline_comment(match):
        exc_type = match.group(1) or 'Exception'
        comment = match.group(2) or ''
        indent = match.group(3)
        var_name = 'e'
        
        # If bare except, use Exception as e
        if not match.group(1):
            exc_part = "Exception as e"
        elif ' as ' not in exc_type:
            exc_part = f"{exc_type} as e"
        else:
            exc_part = exc_type
            var_name = exc_type.split(' as ')[-1].strip()

        log_stmt = f"logging.error(f'Silent error in {os.path.basename(filepath)}: {{str({var_name})}}')"
        
        return f"except {exc_part}:\n{indent}{comment}\n{indent}{log_stmt}"

    # Regex explanation:
    # except\s+([a-zA-Z0-9_\. ]+)?\s*:\s*\n    -> capture exception type (optional)
    # \s*(#.*)?\n                             -> optional comment line
    # (\s+)pass                               -> indent and pass
    
    # This is tricky with regex. Let's try a simpler approach for multiline pass blocks.
    # Matches: except ... :\n <indent> # comment \n <indent> pass
    
    # New attempt for commented pass blocks
    new_content = re.sub(r'except\s*(.*?)\s*:\s*\n(\s*)(#.*)\n\s+pass', 
                         lambda m: f"except {m.group(1) if m.group(1) else 'Exception as e'}:\n{m.group(2)}{m.group(3)}\n{m.group(2)}logging.error(f'Silent error in {os.path.basename(filepath)}: {{str(e)}}')", 
                         content)

    if new_content != content:
        content = ensure_logging(new_content)
        modified = True

    if modified:
        logging.info(f"Fixed {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    count = 0
    for root, dirs, files in os.walk(root_dir):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                fix_file(os.path.join(root, file))
                count += 1
    logging.info(f"Scanned {count} files.")

if __name__ == "__main__":
    main()
