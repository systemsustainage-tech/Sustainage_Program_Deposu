import sys
import os
import sqlite3

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Testing imports...")
try:
    from backend.modules.supplier_portal import supplier_portal_bp
    print("✓ Supplier Portal Blueprint imported")
    
    from backend.modules.reporting.target_manager import TargetManager
    print("✓ Target Manager imported")
    
    # Test DB tables
    tm = TargetManager()
    conn = sqlite3.connect('backend/data/sdg_desktop.sqlite')
    cursor = conn.cursor()
    
    # Check company_targets
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_targets'")
    if cursor.fetchone():
        print("✓ Table 'company_targets' exists")
    else:
        print("✗ Table 'company_targets' MISSING")

    # Check supplier_environmental_data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='supplier_environmental_data'")
    if cursor.fetchone():
        print("✓ Table 'supplier_environmental_data' exists")
    else:
        print("✗ Table 'supplier_environmental_data' MISSING")
        
    conn.close()

except Exception as e:
    print(f"✗ Import/DB Error: {e}")
