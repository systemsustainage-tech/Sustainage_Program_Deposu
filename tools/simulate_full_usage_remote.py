import sys
import os
import logging
import time

# Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Simulation")

def simulate():
    print("DEBUG: Inside simulate() - Starting imports...")
    
    # Setup paths
    sys.path.insert(0, '/var/www/sustainage')
    sys.path.insert(0, '/var/www/sustainage/backend')

    # Import app inside function to avoid global scope execution issues
    try:
        from web_app import app, DB_PATH
        from backend.core.db_log_handler import DBLogHandler
        from security.core.secure_password import hash_password
        import sqlite3
        print("DEBUG: Imports successful.")
    except ImportError as e:
        print(f"Import Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error during import: {e}")
        sys.exit(1)

    print("DEBUG: Proceeding with simulation logic...")

    def ensure_test_user():
        print("Ensuring test user exists...")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ?", ('test_user',))
            user = cursor.fetchone()
            
            if not user:
                print("Creating test_user...")
                password_hash = hash_password('Test1234!')
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, role, is_active, display_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, ('test_user', password_hash, 'test@example.com', 'admin', 1, 'Test User'))
                conn.commit()
                print("test_user created.")
            else:
                print("test_user already exists.")
                
            # Ensure company exists for user
            cursor.execute("SELECT id FROM companies LIMIT 1")
            company = cursor.fetchone()
            if not company:
                print("Creating test company...")
                cursor.execute("INSERT INTO companies (name, created_at) VALUES (?, CURRENT_TIMESTAMP)", ('Test Company',))
                conn.commit()
                company_id = cursor.lastrowid
            else:
                company_id = company[0]
                
            conn.close()
        except Exception as e:
            print(f"Error ensuring test user: {e}")

    ensure_test_user()
    
    print("Starting End-to-End Simulation...")
    client = app.test_client()
    
    # 1. Login
    print("\n--- 1. Login Check ---")
    resp = client.post('/login', data={
        'username': 'test_user',
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    login_success = False
    if resp.status_code == 200:
        if b'/logout' in resp.data or b'Dashboard' in resp.data:
            print("Login successful.")
            login_success = True
        else:
            print("Login response OK, but might be stuck on login page.")
            if b'Giri' in resp.data: # Giriş
                print("Still on login page.")
    else:
        print(f"Login failed with status {resp.status_code}")
        
    if not login_success:
        print("Cannot proceed without login.")
        return

    # 2. Module Availability Check (19 Modules)
    print("\n--- 2. Module Availability Check ---")
    modules = [
        ('/sdg/goals', 'SDG'),
        ('/gri/dashboard', 'GRI'),
        ('/environmental/carbon', 'Carbon'),
        ('/environmental/energy', 'Energy'),
        ('/environmental/water', 'Water'),
        ('/environmental/waste', 'Waste'),
        ('/environmental/biodiversity', 'Biodiversity'),
        ('/social/dashboard', 'Social'),
        ('/governance/dashboard', 'Governance'),
        ('/supply_chain/dashboard', 'Supply Chain'),
        ('/economic/dashboard', 'Economic'),
        ('/esg/dashboard', 'ESG'),
        ('/cbam/dashboard', 'CBAM'),
        ('/csrd/dashboard', 'CSRD'),
        ('/eu_taxonomy/dashboard', 'EU Taxonomy'),
        ('/issb/dashboard', 'ISSB'),
        ('/iirc/dashboard', 'IIRC'),
        ('/esrs/dashboard', 'ESRS'),
        ('/tcfd/dashboard', 'TCFD'),
        ('/tnfd/dashboard', 'TNFD'),
        ('/cdp/dashboard', 'CDP')
    ]
    
    success_count = 0
    failed_modules = []
    
    for route, name in modules:
        try:
            resp = client.get(route, follow_redirects=True)
            if resp.status_code == 200:
                print(f"[OK] {name}")
                success_count += 1
            else:
                print(f"[FAIL] {name} (Status: {resp.status_code})")
                failed_modules.append(name)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            failed_modules.append(name)
            
    print(f"\nModules Operational: {success_count}/{len(modules)}")
    if failed_modules:
        print(f"Failed Modules: {', '.join(failed_modules)}")

    # 3. Report Generation Check
    print("\n--- 3. Unified Report Generation Check ---")
    try:
        resp = client.post('/reports/unified', data={
            'report_name': 'Test Simulation Report',
            'reporting_period': '2024',
            'description': 'Automated test report',
            'modules': ['sdg', 'gri', 'carbon'],
            'include_ai': 'on'
        }, follow_redirects=True)
        
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                print("[SUCCESS] Report generated (Binary content received).")
            elif b'ba\xc5\x9far\xc4\xb1yla' in resp.data: # "başarıyla"
                print("[SUCCESS] Report generation success message received.")
            else:
                print(f"[WARNING] Response 200 but content type ({content_type}) or message unclear.")
        else:
            print(f"[FAIL] Report generation failed (Status: {resp.status_code})")
            
    except Exception as e:
        print(f"[ERROR] Report generation exception: {e}")

if __name__ == "__main__":
    print("DEBUG: Script entry point reached.")
    simulate()
