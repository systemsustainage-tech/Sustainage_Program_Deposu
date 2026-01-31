import re
import os

FILES_TO_SCAN = [
    r"c:\SUSTAINAGESERVER\remote_web_app.py",
    r"c:\SUSTAINAGESERVER\web_app.py",
]

GLOBAL_TABLES = [
    "backup_history", 
    "sqlite_master", 
    "companies",  # Usually accessed by ID or to list all for superadmin
    "users",      # Often accessed for login/profile, handled separately
    "roles",
    "user_roles",
    "sdg_indicators"
]

def scan_file(file_path):
    print(f"\n--- Scanning {os.path.basename(file_path)} ---")
    if not os.path.exists(file_path):
        print("File not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line_clean = line.strip().upper()
        
        is_sql = False
        keywords = ["SELECT ", "UPDATE ", "DELETE FROM ", "INSERT INTO "]
        
        for kw in keywords:
            if kw in line_clean and ("\"" in line or "'" in line):
                is_sql = True
                break
        
        if is_sql:
            # Check if it's operating on a global table
            is_global = False
            for tbl in GLOBAL_TABLES:
                if tbl.upper() in line_clean:
                    is_global = True
                    break
            
            if is_global:
                continue

            # Check for company_id
            if "company_id" not in line and "WHERE" in line_clean:
                 print(f"[{os.path.basename(file_path)}:{i+1}] {line.strip()}")
            elif "company_id" not in line and ("UPDATE" in line_clean or "DELETE" in line_clean):
                 print(f"[{os.path.basename(file_path)}:{i+1}] {line.strip()}")

if __name__ == "__main__":
    for f in FILES_TO_SCAN:
        scan_file(f)
