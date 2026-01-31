import sqlite3
import os
import sys

# Add backend to path to import secure_password
sys.path.append('/var/www/sustainage/backend')
sys.path.append('/var/www/sustainage')

try:
    # Use yonetim.security.core.crypto directly to avoid 'argon2$' prefix added by secure_password wrapper
    from yonetim.security.core.crypto import hash_password
    print("Successfully imported hash_password from yonetim.security.core.crypto")
except ImportError as e:
    print(f"ImportError (yonetim): {e}")
    try:
        from security.core.secure_password import hash_password as hp_wrapped
        # Strip prefix if we must use wrapper
        def hash_password(p):
            h = hp_wrapped(p)
            if h.startswith("argon2$"):
                return h.split("argon2$", 1)[1]
            return h
        print("Using wrapped hash_password with prefix stripping")
    except ImportError:
        print(f"ImportError (wrapper): {e}")
        # Fallback if import fails
    import hashlib
    import secrets
    def hash_password(password):
         salt = secrets.token_hex(16)
         h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
         return f"pbkdf2${salt}:{h}"

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_super_user():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    username = '__super__'
    password = 'Kayra_1507'
    password_hash = hash_password(password)
    
    print(f"Fixing user {username}...")
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    
    if row:
        user_id = row[0]
        print(f"Updating existing user {user_id}...")
        cur.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
    else:
        print("Creating new user...")
        cur.execute("INSERT INTO users (username, password_hash, display_name, email, is_active) VALUES (?, ?, ?, ?, 1)",
                    (username, password_hash, 'Super Admin', 'super@sustainage.app'))
        user_id = cur.lastrowid
        
    # Assign Role
    # Find 'admin' or 'super_admin' role
    cur.execute("SELECT id FROM roles WHERE name IN ('super_admin', 'admin', 'Super Admin') ORDER BY id ASC")
    role_row = cur.fetchone()
    if role_row:
        role_id = role_row[0]
        # Check if user_role exists
        cur.execute("SELECT 1 FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id))
        if not cur.fetchone():
            cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            print(f"Assigned role {role_id} to user.")
    else:
        print("Warning: No admin role found. Creating one...")
        cur.execute("INSERT INTO roles (name, description) VALUES (?, ?)", ('admin', 'Administrator'))
        role_id = cur.lastrowid
        cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
        print(f"Created role admin and assigned to user.")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == '__main__':
    fix_super_user()
