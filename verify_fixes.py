import paramiko
import sys
import re
import os

def verify_fixes():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    files_to_check = {
        'company_edit.html': [
            {'check': "'Şirket Düzenle'", 'desc': "Translation 'Şirket Düzenle'"}
        ],
        'dashboard.html': [
            {'check': "url_for('report_add_page')", 'desc': "Link to report_add_page"},
            {'check': "url_for('companies')", 'desc': "Link to companies"}
        ],
        'data.html': [
            {'check': "url_for('data_add'", 'desc': "Link to data_add"}
        ],
        'data_edit.html': [
            {'check': "data_type", 'desc': "Usage of data_type"}
        ]
    }

    try:
        print("Connecting to server...")
        sys.stdout.flush()
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        print("\n--- VERIFICATION REPORT ---\n")
        
        for filename, checks in files_to_check.items():
            print(f"Checking {filename}...")
            local_path = f"c:\\SUSTAINAGESERVER\\temp_verify_{filename}"
            remote_path = f"/var/www/sustainage/templates/{filename}"
            
            try:
                sftp.get(remote_path, local_path)
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Perform checks
                for item in checks:
                    check_str = item['check']
                    desc = item['desc']
                    
                    if check_str in content:
                        print(f"  [PASS] {desc} found.")
                        # Print context
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if check_str in line:
                                print(f"    Snippet: {line.strip()[:100]}")
                                break
                    else:
                        print(f"  [FAIL] {desc} NOT found.")
                
                # Specific check for data.html to ensure no data_type=
                if filename == 'data.html':
                    if "data_type=" in content:
                        print(f"  [FAIL] Found legacy 'data_type=' parameter in data.html")
                    else:
                        print(f"  [PASS] No legacy 'data_type=' parameter found.")
                
                # Cleanup
                if os.path.exists(local_path):
                    os.remove(local_path)
                    
            except Exception as e:
                print(f"  [ERROR] Could not check {filename}: {e}")
            
            sys.stdout.flush()

        print("\n--- END REPORT ---")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    verify_fixes()
