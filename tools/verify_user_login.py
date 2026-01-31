import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
from backend.yonetim.security.core.crypto import verify_password_compat

def test_admin_login():
    print("Testing admin login...")
    user_manager = UserManager()
    
    # 1. Get user directly from DB to check hash format
    user = user_manager.get_user_by_username('admin')
    if not user:
        print("FAIL: User 'admin' not found.")
        return

    print(f"User found: {user['username']}")
    # print(f"Stored hash prefix: {user['password'][:15]}...")
    print(f"User keys: {user.keys()}")
    
    # Try to find password field
    pwd_field = 'password' if 'password' in user else 'password_hash'
    if pwd_field in user:
         print(f"Stored hash prefix ({pwd_field}): {user[pwd_field][:15]}...")
    else:
         print("WARNING: No password field found in user dict.")

    # 2. Try authentication via verify_password_compat
    pwd_hash = user.get('password_hash') or user.get('password')
    if not pwd_hash:
        print("FAIL: No password hash found.")
        return

    try:
        is_valid = verify_password_compat(pwd_hash, 'admin')
        if is_valid:
            print("SUCCESS: verify_password_compat verified 'admin' password.")
        else:
            print("FAIL: verify_password_compat returned False.")
    except Exception as e:
        print(f"ERROR during verification: {e}")

if __name__ == "__main__":
    test_admin_login()
