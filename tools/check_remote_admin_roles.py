import sqlite3
import os
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_admin_roles():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check users table for admin
        cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if not admin:
            print("User 'admin' not found in users table.")
            return
        
        print(f"Admin User: ID={admin[0]}, Username={admin[1]}")
        admin_id = admin[0]

        # Check user_roles
        print("\nChecking user_roles table...")
        try:
            cursor.execute("""
                SELECT ur.user_id, r.name 
                FROM user_roles ur 
                JOIN roles r ON ur.role_id = r.id 
                WHERE ur.user_id = ?
            """, (admin_id,))
            roles = cursor.fetchall()
            
            existing_role_names = [r[1] for r in roles]
            if roles:
                print("Roles found in user_roles:")
                for r in roles:
                    print(f"  - {r[1]}")
            else:
                print("NO roles found in user_roles table for admin!")

            if 'Super Admin' not in existing_role_names:
                print("'Super Admin' role missing. Adding it...")
                # Check if 'Super Admin' role exists
                cursor.execute("SELECT id FROM roles WHERE name = 'Super Admin'")
                role_row = cursor.fetchone()
                if role_row:
                    role_id = role_row[0]
                    print(f"Found 'Super Admin' role with ID {role_id}. Assigning to admin...")
                    cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (admin_id, role_id))
                    conn.commit()
                    print("Assigned 'Super Admin' role to admin in user_roles.")
                else:
                    print("'Super Admin' role not found in roles table. Creating it...")
                    cursor.execute("INSERT INTO roles (name, display_name, description, is_active) VALUES ('Super Admin', 'Super Admin', 'Full Access', 1)")
                    role_id = cursor.lastrowid
                    cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (admin_id, role_id))
                    conn.commit()
                    print("Created 'Super Admin' role and assigned to admin.")
            else:
                print("'Super Admin' role is already assigned.")

        except sqlite3.OperationalError as e:
            print(f"Error accessing user_roles: {e}")
            # Maybe table doesn't exist?
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_admin_roles()
