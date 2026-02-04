import os
import sqlite3

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def get_verifier():
    try:
        from backend.security.core.secure_password import verify_password
        return verify_password
    except Exception:
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            def verify(stored_hash: str, password: str):
                s = stored_hash
                if s.startswith("argon2$"):
                    s = s.split("argon2$", 1)[1]
                try:
                    ph.verify(s, password)
                    return True, False
                except Exception:
                    return False, False
            return verify
        except Exception:
            return None

def check_user(username: str, password: str):
    print(f"\n--- Checking '{username}' ---")
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, is_active, failed_attempts, locked_until FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        print("User not found.")
        conn.close()
        return
    user_id, stored_hash, is_active, failed, locked = row
    print(f"User ID: {user_id}, Active: {is_active}, Failed: {failed}, Locked: {locked}")
    verifier = get_verifier()
    if not verifier:
        print("No verifier available.")
        conn.close()
        return
    ok, needs = verifier(stored_hash, password)
    print(f"Password OK: {ok}, Needs Rehash: {needs}")
    conn.close()

if __name__ == "__main__":
    check_user("admin", "Admin123!")
    check_user("__super__", "Super123!")
