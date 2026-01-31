
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def check_remote_reports():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Checking /reports page content via curl...")
        # Use cookie file or basic auth if needed? 
        # Actually verify_full_system.py already checked 200 OK.
        # But we want to see the CONTENT. 
        # We can't easily curl with auth session unless we login first.
        # Alternatively, we can check the template file + verify no errors in logs.
        # Let's check the reports.html template first to see if it has Turkish texts.
        
        stdin, stdout, stderr = ssh.exec_command('cat /var/www/sustainage/templates/reports.html')
        content = stdout.read().decode()
        
        if "Raporlar" in content or "Yeni Rapor" in content or "btn_new_report" in content:
            print("Template contains expected keywords.")
            # Check for tr.json keys usage
            if "{{ _('btn_new_report') }}" in content or "{{ _('title_reports') }}" in content:
                 print("Template uses translation keys correctly.")
        else:
             print("WARNING: Template might be missing keywords.")

        # Also check tr.json on remote to ensure keys exist
        stdin, stdout, stderr = ssh.exec_command('grep "btn_new_report" /var/www/sustainage/locales/tr.json')
        tr_check = stdout.read().decode()
        if "btn_new_report" in tr_check:
            print("Translation key 'btn_new_report' FOUND in remote tr.json")
        else:
            print("Translation key 'btn_new_report' MISSING in remote tr.json")

        ssh.close()
    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    check_remote_reports()
