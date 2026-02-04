import os
import sys
import sqlite3
from datetime import datetime

# Paths
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def get_hasher():
    try:
        from backend.security.core.secure_password import hash_password
        return hash_password
    except Exception:
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            def hasher(password):
                return f"argon2${ph.hash(password)}"
            return hasher
        except Exception:
            return None

def reset_super_admin():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure columns exist
    try:
        cur.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
    except Exception as e:
        print(f"Error reading schema: {e}")
        conn.close()
        return

    # Find __super__ account
    cur.execute("SELECT id, username, is_active, failed_attempts, locked_until FROM users WHERE username = '__super__'")
    row = cur.fetchone()
    if not row:
        print("Super Admin '__super__' not found. Creating minimal account...")
        hasher = get_hasher()
        if not hasher:
            print("No hasher available.")
            conn.close()
            return
        pw_hash = hasher("Super123!")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create user record (schema-compatible fields only)
        try:
            cur.execute("""
                INSERT INTO users (username, password_hash, email, is_active, created_at, failed_attempts, must_change_password, is_superadmin)
                VALUES ('__super__', ?, 'super@sustainage.com', 1, ?, 0, 0, 1)
            """, (pw_hash, now))
            conn.commit()
            print("Created '__super__' with password Super123!")
        except Exception as e:
            print(f"Error creating super admin: {e}")
            conn.close()
            return
    else:
        user_id, username, is_active, failed, locked = row
        print(f"Found Super Admin {username} (ID={user_id}) - Active={is_active}, Failed={failed}, Locked={locked}")
        hasher = get_hasher()
        if not hasher:
            print("Hasher not available.")
            conn.close()
            return
        pw_hash = hasher("Super123!")
        # Reset lockout and ensure flags
        try:
            # Build dynamic SET clause based on existing columns
            set_parts = [
                "password_hash = ?",
                "failed_attempts = 0",
                "locked_until = NULL",
                "is_active = 1",
                "must_change_password = 0",
            ]
            params = [pw_hash]
            # Optional super flag column
            if "is_superadmin" in cols:
                set_parts.append("is_superadmin = 1")
            elif "is_super" in cols:
                set_parts.append("is_super = 1")
            set_sql = ", ".join(set_parts)
            cur.execute(f"UPDATE users SET {set_sql} WHERE id = ?", params + [user_id])
            conn.commit()
            print("Super Admin password set to Super123! and lockout cleared.")
        except Exception as e:
            print(f"Error updating super admin: {e}")
            conn.close()
            return

    # Ensure company assignment (company_id via user_companies)
    try:
        cur.execute("SELECT id FROM companies ORDER BY id ASC LIMIT 1")
        c = cur.fetchone()
        if not c:
            cur.execute("INSERT INTO companies (name, sector, country) VALUES ('Sustainage HQ', 'Technology', 'Turkey')")
            company_id = cur.lastrowid
        else:
            company_id = c[0]
        # Fetch super id
        cur.execute("SELECT id FROM users WHERE username='__super__'")
        su = cur.fetchone()
        if su:
            su_id = su[0]
            cur.execute("SELECT 1 FROM user_companies WHERE user_id=? AND company_id=?", (su_id, company_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (?, ?, 1)", (su_id, company_id))
                conn.commit()
                print(f"Assigned company {company_id} to '__super__'.")
    except Exception as e:
        print(f"Company assignment warning: {e}")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    reset_super_admin()
