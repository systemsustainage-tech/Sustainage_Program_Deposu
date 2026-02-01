
import sys
import os
import sqlite3
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from yonetim.kullanici_yonetimi.models.user_manager import UserManager

def verify_audit_logs():
    print("Verifying Audit Logs...")
    
    # Initialize UserManager
    um = UserManager()
    
    # 1. Create Test User
    print("\n1. Creating Test User...")
    user_data = {
        'username': 'audit_test_user',
        'email': 'audit_test@example.com',
        'password': 'Password123!',
        'first_name': 'Audit',
        'last_name': 'Test',
        'company_ids': [1], # Primary company 1
        'role_ids': []
    }
    
    # Clean up first
    conn = um.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", ('audit_test_user',))
    conn.commit()
    conn.close()
    
    created_user_id = um.create_user(user_data, created_by=1)
    if created_user_id > 0:
        print(f"User created with ID: {created_user_id}")
    else:
        print("Failed to create user")
        return

    # 2. Update Test User
    print("\n2. Updating Test User...")
    update_data = {'first_name': 'AuditUpdated'}
    um.update_user(created_user_id, update_data, updated_by=1)
    
    # 3. Delete Test User
    print("\n3. Deleting Test User...")
    um.delete_user(created_user_id, deleted_by=1)
    
    # 4. Create Test Role
    print("\n4. Creating Test Role...")
    role_data = {
        'name': 'audit_test_role',
        'display_name': 'Audit Test Role',
        'description': 'Test role for audit',
        'company_id': 1
    }
    
    # Clean up role
    conn = um.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE name = ?", ('audit_test_role',))
    conn.commit()
    conn.close()
    
    role_id = um.create_role(role_data, created_by=1)
    if role_id > 0:
        print(f"Role created with ID: {role_id}")
    else:
        print("Failed to create role")
        
    # 5. Update Test Role
    print("\n5. Updating Test Role...")
    um.update_role_full(role_id, {'description': 'Updated description'}, updated_by=1)
    
    # 6. Delete Test Role
    print("\n6. Deleting Test Role...")
    um.delete_role(role_id, deleted_by=1)

    # Verify Logs
    print("\nChecking Audit Logs table...")
    conn = um.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT action, resource_type, resource_id, company_id, old_values, new_values 
        FROM audit_logs 
        WHERE resource_id IN (?, ?) OR (resource_type='user' AND resource_id IN (?, ?))
        ORDER BY id ASC
    """, (role_id, created_user_id, created_user_id, role_id))
    
    logs = cursor.fetchall()
    print(f"\nFound {len(logs)} recent logs:")
    for log in logs:
        action, res_type, res_id, cid, old_v, new_v = log
        print(f" - Action: {action}, Type: {res_type}, ID: {res_id}, CompanyID: {cid}")
        # print(f"   Old: {old_v}")
        # print(f"   New: {new_v}")
        
    conn.close()

if __name__ == "__main__":
    verify_audit_logs()
