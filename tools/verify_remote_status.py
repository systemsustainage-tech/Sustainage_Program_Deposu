import sqlite3
import os
import sys

# Add project root to path
sys.path.append('/var/www/sustainage')

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def verify_remote():
    if not os.path.exists(DB_PATH):
        print(f"FAIL: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Verifying Tables ---")
    tables = [
        'users', 'companies', 'licenses', 'audit_logs', 
        'report_templates', 'report_sections', 'report_generation_log', 
        'report_customizations', 'user_companies'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"PASS: Table '{table}' exists. Row count: {count}")
        except sqlite3.OperationalError:
            print(f"FAIL: Table '{table}' DOES NOT EXIST.")

    print("\n--- Verifying Users Schema ---")
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}
        required_columns = [
            'failed_attempts', 'locked_until', 'totp_secret_encrypted', 
            'totp_backup_codes', 'must_change_password'
        ]
        
        for col in required_columns:
            if col in columns:
                print(f"PASS: Column 'users.{col}' exists.")
            else:
                print(f"FAIL: Column 'users.{col}' MISSING.")
    except Exception as e:
        print(f"Error verifying users schema: {e}")

    print("\n--- Verifying Audit Logs ---")
    try:
        # Changed timestamp to created_at based on schema check
        cursor.execute("SELECT action, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 5")
        logs = cursor.fetchall()
        if logs:
            print("Recent Audit Logs:")
            for log in logs:
                print(f" - {log}")
        else:
            print("No audit logs found yet.")
    except Exception as e:
        print(f"Error reading audit logs: {e}")
        
    conn.close()

    print("\n--- Verifying Code Deployment ---")
    web_app_path = '/var/www/sustainage/web_app.py'
    if os.path.exists(web_app_path):
        with open(web_app_path, 'r') as f:
            content = f.read()
            if '_check_two_stage_approval' in content:
                print("PASS: '_check_two_stage_approval' found in web_app.py")
            else:
                print("FAIL: '_check_two_stage_approval' NOT found in web_app.py")
            
            if '@license_check' in content or 'def license_check' in content:
                 print("PASS: 'license_check' found in web_app.py")
            else:
                 print("FAIL: 'license_check' NOT found in web_app.py")
    else:
        print(f"FAIL: {web_app_path} not found.")

if __name__ == "__main__":
    verify_remote()
