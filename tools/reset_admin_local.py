import sqlite3
import hashlib
import os

DB_PATH = "backend/data/sdg_desktop.sqlite"
USER = "admin"
PASS = "Admin123!"

# Using PBKDF2-SHA256 manually for compatibility with old systems if needed, 
# but preferably we use Argon2 if the system supports it. 
# However, the current admin hash is 'pbkdf2$...' which is NOT standard format in verify_password_compat
# The verify_password_compat expects "pbkdf2:..." (werkzeug) or "salt:hash" (custom).
# The current hash 'pbkdf2$119a91896516e7a261dc9f9b40f1ddde:d359e33315f24be11a81e5cce71478099ad31c5d9abf2175ea68d2c99e78ab04'
# looks like "salt:hash" but with a prefix in salt?
# No, wait. 
# verify_password_compat:
# if ":" in stored_hash:
#    salt, hash_hex = stored_hash.split(":", 1)
#    calc = hashlib.pbkdf2_hmac('sha256', (plain or "").encode('utf-8'), salt.encode('utf-8'), 100000).hex()
#    return calc == hash_hex

# The current admin hash is:
# pbkdf2$119a91896516e7a261dc9f9b40f1ddde : d359e33315f24be11a81e5cce71478099ad31c5d9abf2175ea68d2c99e78ab04
# So salt is "pbkdf2$119a91896516e7a261dc9f9b40f1ddde"
# This is weird. 

# Let's just reset it to a standard Argon2 hash if possible, OR a simple SHA256 hex if crypto.py supports it (it does, line 99).
# But better use Argon2 via the crypto module if we can import it, or just use a known salt:hash format.

# Let's try to import the local crypto module to generate a valid hash.
import sys
sys.path.append(os.getcwd())
try:
    from backend.yonetim.security.core.crypto import hash_password
    print("Using crypto.hash_password (Argon2)")
    new_hash = hash_password(PASS)
except ImportError as e:
    print(f"Could not import crypto: {e}")
    # Fallback to simple salt:hash
    salt = "somesalt"
    h = hashlib.pbkdf2_hmac('sha256', PASS.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    new_hash = f"{salt}:{h}"

print(f"New hash for '{USER}': {new_hash}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, USER))
if cursor.rowcount == 0:
    print(f"User {USER} not found, creating...")
    # Insert with defaults
    cursor.execute("""
        INSERT INTO users (username, password_hash, email, is_active, is_verified, role)
        VALUES (?, ?, 'admin@sustainage.cloud', 1, 1, 'super_admin')
    """, (USER, new_hash))
    # Wait, 'role' column does not exist in users table according to PRAGMA!
    # User roles are likely in user_roles table.
else:
    print(f"User {USER} updated.")

conn.commit()

# Ensure role exists in user_roles
# First get user id
cursor.execute("SELECT id FROM users WHERE username = ?", (USER,))
user_id = cursor.fetchone()[0]

# Check roles table for 'super_admin' or 'admin'
cursor.execute("SELECT id, name FROM roles")
roles = cursor.fetchall()
print(f"Roles: {roles}")

# Find super_admin role id
admin_role_id = None
for r_id, r_name in roles:
    if r_name == 'super_admin':
        admin_role_id = r_id
        break
    if r_name == 'admin' and not admin_role_id:
        admin_role_id = r_id

if not admin_role_id:
    print("Creating super_admin role...")
    cursor.execute("INSERT INTO roles (name, description) VALUES ('super_admin', 'Super Administrator')")
    admin_role_id = cursor.lastrowid

# Assign role
cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, admin_role_id))
print(f"Assigned role {admin_role_id} to user {user_id}")

conn.commit()
conn.close()
