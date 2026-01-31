import os
import sys
import sqlite3
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)
DB_PATH = os.path.join(BACKEND_DIR, 'data', 'sdg_desktop.sqlite')

def check_db():
    print("\n--- Checking Database ---")
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        tables = [
            'users', 'companies', 'report_registry', 
            'carbon_emissions', 'energy_consumption', 'water_consumption', 'waste_generation',
            'tnfd_recommendations'
        ]
        missing = []
        for t in tables:
            try:
                conn.execute(f"SELECT 1 FROM {t} LIMIT 1")
                logging.info(f"Table '{t}' exists.")
            except sqlite3.OperationalError:
                missing.append(t)
                logging.error(f"Table '{t}' is MISSING.")
        
        conn.close()
        if missing:
            return False
        return True
    except Exception as e:
        logging.error(f"DB Check Failed: {e}")
        return False

def check_modules():
    print("\n--- Checking Module Imports ---")
    modules = [
        'modules.sdg.sdg_manager',
        'modules.gri.gri_manager',
        'modules.social.social_manager',
        'modules.governance.corporate_governance',
        'modules.environmental.carbon_manager',
        'modules.environmental.energy_manager',
        'modules.esg.esg_manager',
        'modules.cbam.cbam_manager',
        'modules.csrd.csrd_compliance_manager',
        'modules.eu_taxonomy.taxonomy_manager',
        'modules.environmental.waste_manager',
        'modules.environmental.water_manager',
        'modules.environmental.biodiversity_manager',
        'modules.economic.economic_value_manager',
        'modules.economic.supply_chain_manager',
        'modules.cdp.cdp_manager',
        'modules.issb.issb_manager',
        'modules.iirc.iirc_manager',
        'modules.esrs.esrs_manager',
        'modules.tcfd.tcfd_manager'
    ]
    
    failed = []
    for m in modules:
        try:
            __import__(m)
            logging.info(f"Imported {m}")
        except ImportError as e:
            logging.error(f"Failed to import {m}: {e}")
            failed.append(m)
        except Exception as e:
            logging.error(f"Error importing {m}: {e}")
            failed.append(m)
            
    if failed:
        return False
    return True

def check_ai():
    print("\n--- Checking AI Module ---")
    try:
        from modules.ai.ai_manager import AIManager
        logging.info("AIManager module imported successfully.")
        return True
    except Exception as e:
        logging.error(f"AI Check Failed: {e}")
        return False

def check_mail():
    print("\n--- Checking Mail System ---")
    try:
        from services.email_service import EMAIL_CONFIG
        logging.info(f"Email Config Loaded: {EMAIL_CONFIG.get('smtp_server')}")
        return True
    except Exception as e:
        logging.error(f"Mail Check Failed: {e}")
        return False

def check_routes():
    print("\n--- Checking Web Routes ---")
    routes = [
        '/', '/login', '/dashboard', '/users', '/companies', '/reports', '/data',
        '/sdg', '/gri', '/social', '/governance', '/carbon', '/energy', '/esg',
        '/cbam', '/csrd', '/taxonomy', '/waste', '/water', '/biodiversity',
        '/economic', '/supply_chain', '/cdp', '/issb', '/iirc', '/esrs', '/tcfd', '/tnfd'
    ]
    
    base_url = "http://127.0.0.1:5000"
    failed = []
    
    for r in routes:
        try:
            resp = requests.get(f"{base_url}{r}", timeout=5)
            # Redirect to login (302) or success (200) is fine. 500 is bad.
            if resp.status_code in [200, 302]:
                logging.info(f"Route {r}: OK ({resp.status_code})")
            else:
                logging.error(f"Route {r}: FAILED ({resp.status_code})")
                failed.append(r)
        except Exception as e:
            logging.error(f"Route {r}: ERROR ({e})")
            failed.append(r)
            
    if failed:
        return False
    return True

def main():
    print("Starting Full System Verification...")
    db_ok = check_db()
    mods_ok = check_modules()
    ai_ok = check_ai()
    mail_ok = check_mail()
    routes_ok = check_routes()
    
    print("\n\n=== VERIFICATION SUMMARY ===")
    print(f"Database: {'OK' if db_ok else 'FAIL'}")
    print(f"Modules: {'OK' if mods_ok else 'FAIL'}")
    print(f"AI System: {'OK' if ai_ok else 'FAIL'}")
    print(f"Mail System: {'OK' if mail_ok else 'FAIL'}")
    print(f"Web Routes: {'OK' if routes_ok else 'FAIL'}")
    
    if db_ok and mods_ok and ai_ok and mail_ok and routes_ok:
        print("\nSUCCESS: System is fully functional.")
        sys.exit(0)
    else:
        print("\nFAILURE: System has issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
