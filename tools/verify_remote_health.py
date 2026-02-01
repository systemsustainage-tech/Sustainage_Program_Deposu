import paramiko
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

CHECK_SCRIPT = """
import sys
import os
import logging
from flask import g

# Setup path
sys.path.append('/var/www/sustainage')

print("Importing web_app...", flush=True)
try:
    from web_app import app, MANAGERS
    print("Import complete.", flush=True)
except Exception as e:
    print(f"CRITICAL: Failed to import web_app: {e}", flush=True)
    sys.exit(1)

# Disable detailed logging for clean output
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def check_modules():
    print("Starting module verification...", flush=True)
    
    # Critical Endpoints to check
    endpoints = [
        # Dashboard & Core
        ('/dashboard', 'Dashboard'),
        ('/settings', 'Settings'),
        ('/data', 'Data Entry'),
        
        # Modules
        ('/governance', 'Governance'),
        ('/human_rights', 'Human Rights'),
        ('/labor', 'Labor Practices'),
        ('/environment', 'Environment'),
        ('/fair_operating', 'Fair Operating'),
        ('/consumer', 'Consumer Issues'),
        ('/community', 'Community'),
        
        # New/Updated Modules
        ('/training', 'Training'),
        ('/biodiversity', 'Biodiversity'),
        ('/economic', 'Economic'),
        ('/supply_chain', 'Supply Chain'),
        ('/waste', 'Waste'),
        ('/water', 'Water'),
        ('/carbon', 'Carbon'),
        ('/energy', 'Energy'),
        ('/esg', 'ESG Score'),
        ('/benchmark', 'Benchmark'),
        ('/regulation', 'Regulation'),
        
        # Reporting
        ('/reporting', 'Reporting'),
        ('/analysis', 'Analysis')
    ]
    
    with app.test_client() as client:
        # Simulate Login
        with client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'admin', 'role': 'admin', 'is_super': True}
            sess['company_id'] = 1
            sess['company_name'] = 'Sustainage Test'
            sess['_fresh'] = True
        
        passed = []
        failed = []
        
        for url, name in endpoints:
            try:
                # We need to manually set g.company_id if test_client doesn't trigger before_request correctly for context
                # But Flask test client should handle session.
                # However, our @require_company_context uses g.company_id which is set in before_request
                
                res = client.get(url, follow_redirects=True)
                
                if res.status_code == 200:
                    passed.append(name)
                elif res.status_code == 302:
                     # Redirect usually means login required or missing context
                     failed.append(f"{name} (302 Redirect -> {res.location})")
                else:
                    failed.append(f"{name} ({res.status_code})")
            except Exception as e:
                failed.append(f"{name} (Exception: {str(e)})")
        
        print("-" * 30)
        print(f"TOTAL: {len(endpoints)}")
        print(f"PASSED: {len(passed)}")
        print(f"FAILED: {len(failed)}")
        print("-" * 30)
        
        if failed:
            print("FAILED MODULES:")
            for f in failed:
                print(f" - {f}")
            sys.exit(1)
        else:
            print("ALL MODULES OPERATIONAL.")
            sys.exit(0)

if __name__ == "__main__":
    check_modules()
"""

def verify_remote():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS, look_for_keys=False, allow_agent=False)
        
        print("Connected to server.")
        
        # Create remote script
        remote_script_path = '/tmp/verify_modules.py'
        sftp = ssh.open_sftp()
        with sftp.file(remote_script_path, 'w') as f:
            f.write(CHECK_SCRIPT)
        sftp.close()
        
        print("Running verification script on remote server...")
        # Run with venv python
        cmd = f"/var/www/sustainage/venv/bin/python -u {remote_script_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("\n--- OUTPUT ---")
        print(out)
        
        if err:
            print("\n--- ERRORS ---")
            print(err)
            
        ssh.close()
        
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    verify_remote()
