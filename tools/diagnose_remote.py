
import sys
import os
import logging
import sqlite3

# Setup paths
sys.path.append('/var/www/sustainage')
sys.path.append('/var/www/sustainage/backend')

print("!!! DIAGNOSE REMOTE RUNNING v4 !!!")
print(f"CWD: {os.getcwd()}")

DESKTOP_DB = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
print(f"Checking existence of: {DESKTOP_DB}")
exists = os.path.exists(DESKTOP_DB)
print(f"Exists: {exists}")

if exists:
    DB_PATH = DESKTOP_DB
else:
    print(f"⚠️ {DESKTOP_DB} not found, falling back to sustainage.db")
    DB_PATH = '/var/www/sustainage/sustainage.db'

print(f"Selected DB_PATH: {DB_PATH}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Diagnose")

def test_manager(name, class_name, module_path):
    print(f"\n--- Testing {name} ({class_name}) ---")
    try:
        module = __import__(module_path, fromlist=[class_name])
        ManagerClass = getattr(module, class_name)
        manager = ManagerClass(DB_PATH)
        print(f"✅ Initialization successful")
        return manager
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

def main():
    print(f"Using DB_PATH in main: {DB_PATH}")
    
    # Check if tables exist
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Database has {len(tables)} tables.")
        
        required_tables = ['targets', 'energy_consumption', 'biodiversity_projects', 'social_employees', 'supply_chain_suppliers']
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' MISSING")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    # 1. TargetManager
    tm = test_manager("TargetManager", "TargetManager", "backend.modules.reporting.target_manager")
    if tm:
        try:
            targets = tm.get_targets(1) # company_id=1
            print(f"✅ get_targets(1) returned {len(targets)} targets")
            for t in targets:
                print(f"  - Target: {t['name']} (Status: {t.get('status')})")
        except Exception as e:
            print(f"❌ get_targets failed: {e}")

    # 2. EnergyManager
    em = test_manager("EnergyManager", "EnergyManager", "backend.modules.environmental.energy_manager")
    if em:
        try:
            stats = em.get_dashboard_stats(1)
            print(f"✅ get_dashboard_stats(1) returned: {stats}")
        except Exception as e:
            print(f"❌ get_dashboard_stats failed: {e}")

if __name__ == "__main__":
    main()
