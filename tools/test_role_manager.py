import sys
import os
import sqlite3

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from core.role_manager import RoleManager
from config.database import DB_PATH

def test_role_manager():
    print(f"Testing RoleManager with DB: {DB_PATH}", flush=True)
    rm = RoleManager()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Setup test data
    try:
        # Create test user
        cursor.execute("INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES ('test_role_user', 'test@role.com', 'dummyhash', 'Test', 'User')")
        user_id = cursor.lastrowid
        conn.commit()
        print(f"Created test user ID: {user_id}", flush=True)
        
        # Create Role
        role_id = rm.create_role("Test Editor", "Can edit things")
        if not role_id:
            raise Exception("Failed to create role")
        print(f"Created role ID: {role_id}", flush=True)
        
        # Assign Permission
        rm.assign_permission_to_role(role_id, "gri.read")
        rm.assign_permission_to_role(role_id, "gri.update")
        print("Assigned permissions to role.")
        
        # Assign Role to User
        # Need to use role name for the helper method, or direct insert?
        # Helper uses name.
        rm.assign_role_to_user(user_id, "Test Editor")
        print("Assigned role to user.")
        
        # Checks
        has_read = rm.check_permission(user_id, "gri.read")
        has_delete = rm.check_permission(user_id, "gri.delete")
        
        print(f"Check gri.read (Expect True): {has_read}")
        print(f"Check gri.delete (Expect False): {has_delete}")
        
        assert has_read == True
        assert has_delete == False
        
        print("Test PASSED.")
        
    except Exception as e:
        print(f"Test FAILED: {e}")
    finally:
        # Cleanup
        try:
            if 'user_id' in locals():
                cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if 'role_id' in locals():
                cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
                cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
            conn.commit()
        except:
            pass
        conn.close()

if __name__ == "__main__":
    test_role_manager()
