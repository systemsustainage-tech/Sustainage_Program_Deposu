
import requests
import re
import paramiko
import sqlite3
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_remote_db_mappings():
    print("\n--- Checking Remote Mapping Tables ---")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check if mapping file exists
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/sustainage/mapping/sdg_gri_mapping.py")
        print(f"Mapping file check: {stdout.read().decode().strip()}")
        
        # Check DB tables
        cmd = f"sqlite3 {DB_PATH} \".tables\""
        stdin, stdout, stderr = client.exec_command(cmd)
        tables = stdout.read().decode()
        print(f"Tables found: {tables}")
        
        if "sdg_gri_links" in tables or "sdg_mappings" in tables:
            print("[OK] SDG mapping table found.")
        else:
            print("[WARN] SDG mapping table NOT found.")
            
    except Exception as e:
        print(f"[ERROR] SSH/DB Check failed: {e}")
    finally:
        client.close()

def login_and_verify_http():
    print("\n--- Verifying HTTP Routes ---")
    url = "http://72.62.150.207/login"
    payload = {
        "username": "__super__",
        "password": "Kayra_1507"
    }
    s = requests.Session()
    try:
        r = s.post(url, data=payload, allow_redirects=True)
        if r.status_code == 200:
            if "Dashboard" in r.text or "Sürdürülebilirlik Paneli" in r.text:
                print("[OK] Login successful.")
                
                # Check SDG
                r_sdg = s.get("http://72.62.150.207/sdg")
                if "Sürdürülebilir Kalkınma Amaçları" in r_sdg.text:
                    print("[OK] /sdg page loaded correctly.")
                else:
                    print("[WARN] /sdg page content missing.")
                    print(r_sdg.text[:200])
                    
            else:
                print("[FAIL] Login failed (Dashboard not found).")
                if "Kullanıcı adı veya parola hatalı" in r.text:
                    print("Reason: Invalid credentials.")
                elif "Sistem hatası" in r.text:
                    print("Reason: System error (User Manager disabled?).")
                elif "Hesabınız kilitli" in r.text:
                    print("Reason: Account locked.")
                else:
                    print("Reason: Unknown.")
                    # print(r.text[:500]) 
    except Exception as e:
        print(f"[ERROR] HTTP Request failed: {e}")

if __name__ == "__main__":
    check_remote_db_mappings()
    login_and_verify_http()
