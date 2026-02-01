
import sys
import os
import sqlite3
import json

# Add project root and backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
from config.database import DB_PATH

def verify_role_isolation():
    print(f"Database: {DB_PATH}")
    um = UserManager(DB_PATH)
    
    # 1. Setup Test Companies
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create two test companies if not exist
    cursor.execute("INSERT OR IGNORE INTO companies (id, name, is_active) VALUES (998, 'Test Company A', 1)")
    cursor.execute("INSERT OR IGNORE INTO companies (id, name, is_active) VALUES (999, 'Test Company B', 1)")
    conn.commit()
    conn.close()
    
    print("Test companies created/verified.")
    
    # Pre-cleanup
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE name IN ('custom_role_a', 'custom_role_b')")
    conn.commit()
    conn.close()
    
    # 2. Create Custom Role for Company A
    role_data_a = {
        'name': 'custom_role_a',
        'display_name': 'Custom Role A',
        'description': 'Role for Company A',
        'is_system_role': False,
        'is_active': True,
        'company_id': 998,
        'permission_ids': []
    }
    
    role_id_a = um.create_role(role_data_a, created_by=1)
    print(f"Created Role A (ID: {role_id_a}) for Company A")
    
    # 3. Create Custom Role for Company B
    role_data_b = {
        'name': 'custom_role_b',
        'display_name': 'Custom Role B',
        'description': 'Role for Company B',
        'is_system_role': False,
        'is_active': True,
        'company_id': 999,
        'permission_ids': []
    }
    
    role_id_b = um.create_role(role_data_b, created_by=1)
    print(f"Created Role B (ID: {role_id_b}) for Company B")
    
    # 4. Verify get_roles for Company A
    roles_a = um.get_roles(company_id=998)
    role_names_a = [r['name'] for r in roles_a]
    print(f"\nRoles for Company A: {role_names_a}")
    
    if 'custom_role_a' in role_names_a and 'custom_role_b' not in role_names_a:
        print("PASS: Company A sees its own role and not Company B's.")
    else:
        print("FAIL: Company A visibility check failed.")
        
    # 5. Verify get_roles for Company B
    roles_b = um.get_roles(company_id=999)
    role_names_b = [r['name'] for r in roles_b]
    print(f"\nRoles for Company B: {role_names_b}")
    
    if 'custom_role_b' in role_names_b and 'custom_role_a' not in role_names_b:
        print("PASS: Company B sees its own role and not Company A's.")
    else:
        print("FAIL: Company B visibility check failed.")
        
    # 6. Verify System Roles Visibility
    # Assuming 'admin' or 'super_admin' is a system role
    if 'admin' in role_names_a and 'admin' in role_names_b:
        print("PASS: System roles are visible to both.")
    else:
        print("FAIL: System roles visibility check failed (or 'admin' role missing).")

    # Cleanup
    # um.delete_role(role_id_a) # Soft delete
    # um.delete_role(role_id_b) # Soft delete
    
    # Hard delete for test cleanup
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if role_id_a > 0:
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id_a,))
    if role_id_b > 0:
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id_b,))
    
    # Also clean up any lingering roles with these names from previous failed runs
    cursor.execute("DELETE FROM roles WHERE name IN ('custom_role_a', 'custom_role_b')")
    
    conn.commit()
    conn.close()
    
    print("\nTest roles cleaned up (hard delete).")

if __name__ == "__main__":
    verify_role_isolation()
