import os
import sys
import logging
import sqlite3

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
from backend.yonetim.security.core.crypto import hash_password, verify_password_compat

def test_login():
    um = UserManager()
    
    # 1. Test Admin Login
    print("\n--- Testing Admin Login ---")
    admin = um.get_user_by_username('admin')
    if admin:
        print(f"Admin found: {admin['username']}")
        print(f"Hash: {admin.get('password_hash')}")
        
        # Test with known password
        password = "Admin_2025!"
        success = um.authenticate('admin', password)
        print(f"Login with '{password}': {'SUCCESS' if success else 'FAILED'}")
        
        if not success:
            print("Direct verification test:")
            try:
                print(f"Verify result: {verify_password_compat(admin['password_hash'], password)}")
            except Exception as e:
                print(f"Verify exception: {e}")
    else:
        print("Admin user not found!")

    # 2. Test New User Creation and Login
    print("\n--- Testing New User Creation ---")
    new_username = f"testuser_{os.urandom(4).hex()}"
    password = "Test_1234!"
    
    user_data = {
        'username': new_username,
        'email': f"{new_username}@example.com",
        'password': password,
        'first_name': 'Test',
        'last_name': 'User',
        'role_ids': [] # Default role
    }
    
    try:
        user_id = um.create_user(user_data, created_by=1)
        print(f"Created user {new_username} with ID {user_id}")
        
        if user_id > 0:
            # Verify immediately
            user = um.get_user_by_id(user_id)
            print(f"User stored hash: {user['password_hash']}")
            
            # Auth test
            auth_result = um.authenticate(new_username, password)
            print(f"Auth result: {'SUCCESS' if auth_result else 'FAILED'}")
            
            if not auth_result:
                 print("Direct verification test:")
                 try:
                    print(f"Verify result: {verify_password_compat(user['password_hash'], password)}")
                 except Exception as e:
                    print(f"Verify exception: {e}")
        else:
            print("Failed to create user (ID <= 0)")
            
    except Exception as e:
        print(f"Error creating user: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    test_login()
