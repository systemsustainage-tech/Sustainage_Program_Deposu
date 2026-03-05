
import os
import sys

def check_file(path, description):
    if os.path.exists(path):
        print(f"[OK] {description} found: {path}")
        return True
    else:
        print(f"[FAIL] {description} MISSING: {path}")
        return False

def verify_docs_setup():
    print("--- Verifying Documentation & Setup Requirements ---\n")
    
    # 1. Check Documentation Files
    docs = [
        ("docs/DEVELOPER_GUIDE.md", "Developer Guide"),
        ("docs/ADMIN_GUIDE.md", "Admin Guide"),
        ("docs/INSTALLATION.md", "Installation Guide"),
        ("docs/API_REFERENCE.md", "API Reference"),
        ("docs/USER_MANUAL.md", "User Manual")
    ]
    
    all_docs_ok = True
    for path, desc in docs:
        if not check_file(path, desc):
            all_docs_ok = False
            
    # 2. Check Configuration Files mentioned in docs
    configs = [
        ("prometheus.yml", "Prometheus Config"),
        ("requirements.txt", "Python Requirements"),
        ("package.json", "Frontend Package Config") # In frontend/
    ]
    
    # Adjust path for frontend package.json
    if os.path.exists("frontend/package.json"):
        print(f"[OK] Frontend Package Config found: frontend/package.json")
    else:
        print(f"[FAIL] Frontend Package Config MISSING: frontend/package.json")
        all_docs_ok = False

    for path, desc in configs:
        if path == "package.json": continue # Handled above
        if not check_file(path, desc):
            all_docs_ok = False
            
    print("\n--- Verification Result ---")
    if all_docs_ok:
        print("SUCCESS: All documentation and critical setup files are present.")
        sys.exit(0)
    else:
        print("FAILURE: Some files are missing.")
        sys.exit(1)

if __name__ == "__main__":
    verify_docs_setup()
