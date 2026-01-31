
import sqlite3
import os
import sys

# Add backend to path to import crypto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from yonetim.security.core.crypto import verify_password_compat
from config.database import DB_PATH

def check_admin():
    print(f"Checking DB: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, is_active FROM users WHERE username='admin'")
    row = cur.fetchone()
    conn.close()

    if not row:
        print("Admin user not found!")
        return

    uid, username, pwd_hash, active = row
    print(f"User: {username} (ID: {uid})")
    print(f"Active: {active}")
    print(f"Hash: {pwd_hash[:30]}...")

    # Verify
    password = "Admin_2025!"
    try:
        is_valid = verify_password_compat(pwd_hash, password)
        print(f"Password '{password}' valid? {is_valid}")
    except Exception as e:
        print(f"Verification error: {e}")

if __name__ == "__main__":
    check_admin()
