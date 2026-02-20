import shutil
import os

PROJECT_ROOT = r"c:\SUSTAINAGESERVER"
LOCALES_SRC = os.path.join(PROJECT_ROOT, "locales")
FRONTEND_LOCALES_DEST = os.path.join(PROJECT_ROOT, "frontend", "src", "locales")

def prepare_build():
    print("Preparing Frontend Build...")
    
    if not os.path.exists(LOCALES_SRC):
        print(f"Error: Source locales not found at {LOCALES_SRC}")
        return

    if not os.path.exists(FRONTEND_LOCALES_DEST):
        try:
            os.makedirs(FRONTEND_LOCALES_DEST)
            print(f"Created directory: {FRONTEND_LOCALES_DEST}")
        except Exception as e:
             # It might be that frontend dir doesn't exist if not cloned
             print(f"Warning: Could not create {FRONTEND_LOCALES_DEST}. Is frontend folder present? {e}")
             return
        
    # Copy JSON files
    count = 0
    for filename in os.listdir(LOCALES_SRC):
        if filename.endswith(".json"):
            src = os.path.join(LOCALES_SRC, filename)
            dst = os.path.join(FRONTEND_LOCALES_DEST, filename)
            shutil.copy2(src, dst)
            print(f"Copied {filename} to frontend locales.")
            count += 1
            
    print(f"Frontend locales synced ({count} files).")

if __name__ == "__main__":
    prepare_build()
