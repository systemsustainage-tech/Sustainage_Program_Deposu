import os
import re

def fix_init_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == '__init__.py':
                file_path = os.path.join(root, file)
                process_file(file_path)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    modified = False
    
    # Regex to match: from .xyz_gui import XyzGUI  OR  from modules.xyz.xyz_gui import XyzGUI
    # Capture groups: 1=indentation, 2=full_import_line, 3=class_name
    import_pattern = re.compile(r'^(\s*)(from\s+[\w\.]+_gui\s+import\s+([\w, ]+))')
    
    # Also match direct imports like: import backend.modules.xyz.xyz_gui as gui
    # But usually __init__.py uses 'from ... import ...'
    
    for line in lines:
        match = import_pattern.match(line)
        if match:
            indent = match.group(1)
            full_import = match.group(2)
            imported_names = match.group(3)
            
            # Split names if multiple (e.g. "GUI1, GUI2")
            names = [n.strip() for n in imported_names.split(',')]
            
            # Create the replacement
            replacement = [
                f"{indent}try:\n",
                f"{indent}    {full_import}\n",
                f"{indent}except ImportError:\n"
            ]
            for name in names:
                # Handle 'as' alias: "MyGUI as GUI" -> name="MyGUI as GUI"
                if ' as ' in name:
                    alias = name.split(' as ')[1].strip()
                    replacement.append(f"{indent}    {alias} = None\n")
                else:
                    replacement.append(f"{indent}    {name} = None\n")
            
            new_lines.extend(replacement)
            modified = True
            print(f"Fixed: {file_path} -> {full_import.strip()}")
        else:
            new_lines.append(line)
            
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

if __name__ == '__main__':
    fix_init_files('c:/SDG/server/backend/modules')
