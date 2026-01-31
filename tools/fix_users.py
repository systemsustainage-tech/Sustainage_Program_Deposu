import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.yonetim.security.core.crypto import hash_password
except ImportError:
    # Try alternate import for remote execution structure
    sys.path.append('/var/www/sustainage')
    from backend.yonetim.security.core.crypto import hash_password

def fix_users():
    # Priority list of databases to check and update
    db_paths = [
        'sustainage.db',
        'backend/data/sdg_desktop.sqlite',
        '/var/www/sustainage/sustainage.db',
        '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    ]
    
    updated_count = 0
    for path in db_paths:
        if not os.path.isabs(path):
             path = os.path.abspath(path)
             
        if not os.path.exists(path):
            continue
            
        print(f"--- Updating database: {path} ---")
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            
            # Check if users table exists
            try:
                cursor.execute("SELECT 1 FROM users LIMIT 1")
            except sqlite3.OperationalError:
                print("Users table not found, skipping.")
                conn.close()
                continue

            users_to_fix = [
                ('admin', 'admin'),
                ('__super__', 'super_admin')
            ]

            for username, password in users_to_fix:
                try:
                    new_hash = hash_password(password)
                    
                    # Check if user exists
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    row = cursor.fetchone()
                    user_id = None
                    
                    if not row:
                        print(f"User {username} not found. Creating...")
                        try:
                            # Basic user creation without role column
                            cursor.execute("""
                                INSERT INTO users (username, password_hash, email, first_name, last_name, is_active, created_at)
                                VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
                            """, (username, new_hash, f"{username}@example.com", username.capitalize(), "User"))
                            user_id = cursor.lastrowid
                            print(f"User {username} created with ID {user_id}.")
                        except Exception as e:
                            print(f"Error creating {username}: {e}")
                            continue
                    else:
                        user_id = row[0]
                        print(f"Resetting {username} password to '{password}'...")
                        # Reset password, activate, and clear lockouts
                        try:
                            cursor.execute("UPDATE users SET password_hash = ?, is_active = 1, failed_attempts = 0, locked_until = NULL WHERE username = ?", (new_hash, username))
                        except Exception:
                            # Fallback if columns missing
                            cursor.execute("UPDATE users SET password_hash = ?, is_active = 1 WHERE username = ?", (new_hash, username))
                            
                        if cursor.rowcount > 0:
                            print(f"{username} password updated, activated, and unlocked.")
                        else:
                            print(f"{username} not found.")

                    # Assign Role
                    if user_id:
                        role_name = 'super_admin' if username == '__super__' else 'admin'
                        # Find role ID
                        cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
                        role_row = cursor.fetchone()
                        if role_row:
                            role_id = role_row[0]
                            # Check if user_role exists
                            cursor.execute("SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
                            if not cursor.fetchone():
                                try:
                                    cursor.execute("INSERT INTO user_roles (user_id, role_id, created_at) VALUES (?, ?, datetime('now'))", (user_id, role_id))
                                    print(f"Assigned role {role_name} (ID {role_id}) to user {username}.")
                                except Exception as e:
                                    # Try without created_at if fails
                                    try:
                                        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
                                        print(f"Assigned role {role_name} (ID {role_id}) to user {username}.")
                                    except Exception as ex:
                                        print(f"Error assigning role: {ex}")
                        else:
                            print(f"Role {role_name} not found!")
                            
                except Exception as e:
                    print(f"Error processing {username}: {e}")

            conn.commit()
            conn.close()
            updated_count += 1
        except Exception as e:
            print(f"Error processing {path}: {e}")
            
    if updated_count == 0:
        print("No databases updated!")

if __name__ == "__main__":
    fix_users()
