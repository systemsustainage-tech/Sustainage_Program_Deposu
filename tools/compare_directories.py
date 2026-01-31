import os

DIR1 = r"c:\sdg"
DIR2 = r"c:\SUSTAINAGESERVER"

SKIP_DIRS = {'.git', '.trae', '__pycache__', 'venv', 'node_modules', '.idea', '.vscode', 'tmp', 'temp', 'logs', 'tools', '.mypy_cache', '.github', 'archive'}
SKIP_EXTENSIONS = {'.pyc', '.log', '.tmp', '.bak', '.txt', '.md', '.csv', '.xlsx'}
INTERESTING_EXTENSIONS = {'.py', '.php', '.html', '.json', '.js', '.css'}

def compare_dirs(dir1, dir2):
    missing_in_dir2 = []
    
    for root, dirs, files in os.walk(dir1):
        # Skip hidden/ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        rel_path = os.path.relpath(root, dir1)
        
        # Only care about specific important directories
        if rel_path == "." or rel_path.startswith("tools") or rel_path.startswith("tests") or rel_path.startswith("scripts") or rel_path.startswith("deploy"):
             continue
             
        target_dir = os.path.join(dir2, rel_path)
        
        if not os.path.exists(target_dir):
            missing_in_dir2.append(f"DIRECTORY: {rel_path}")
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in INTERESTING_EXTENSIONS:
                continue
                
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            if not os.path.exists(dst_file):
                missing_in_dir2.append(f"FILE: {os.path.join(rel_path, file)}")

    return missing_in_dir2

if __name__ == "__main__":
    print(f"Comparing {DIR1} to {DIR2}...")
    missing = compare_dirs(DIR1, DIR2)
    
    print("\n--- MISSING ITEMS IN SUSTAINAGESERVER ---")
    for item in missing[:100]:  # Limit output
        print(item)
    
    if len(missing) > 100:
        print(f"\n... and {len(missing) - 100} more items.")
