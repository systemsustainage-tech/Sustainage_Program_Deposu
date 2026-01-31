
import os
import shutil

SOURCE_DIR = r"c:\sdg\config"
DEST_DIR = r"c:\SUSTAINAGESERVER\config"
SKIP_FILES = ["database.py", "settings.py"]

def sync_config():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    files = os.listdir(SOURCE_DIR)
    for f in files:
        if f in SKIP_FILES:
            print(f"Skipping {f}")
            continue
            
        src_path = os.path.join(SOURCE_DIR, f)
        dest_path = os.path.join(DEST_DIR, f)
        
        if os.path.isfile(src_path):
            try:
                shutil.copy2(src_path, dest_path)
                print(f"Copied {f}")
            except Exception as e:
                print(f"Error copying {f}: {e}")

if __name__ == "__main__":
    sync_config()
