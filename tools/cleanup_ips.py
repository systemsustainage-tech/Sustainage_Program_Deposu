import os

WRONG_IP = "72.62.150.207"
CORRECT_IP = "72.62.150.207"

def cleanup_directory(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        if ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if not file.endswith(('.py', '.md', '.json', '.txt')):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if WRONG_IP in content:
                    print(f"Fixing {file_path}...")
                    new_content = content.replace(WRONG_IP, CORRECT_IP)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return count

if __name__ == "__main__":
    print("Starting IP cleanup...")
    c_tools = cleanup_directory("c:\\SUSTAINAGESERVER\\tools")
    c_root = cleanup_directory("c:\\SUSTAINAGESERVER")
    print(f"Cleanup complete. Fixed {c_tools + c_root} files.")
