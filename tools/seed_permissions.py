import sqlite3
import os
import datetime

# Adjust path to your DB
DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

MODULES = [
    'sdg', 'gri', 'esg', 'carbon', 'water', 'waste', 'cdp', 'cbam', 
    'eu_taxonomy', 'tcfd', 'tnfd', 'sasb', 'ifrs', 'iirc', 'skdm', 
    'iso', 'bist', 'ungc', 'social', 'governance', 'economic',
    'user_management', 'role_management', 'system_settings', 'audit_logs'
]

ACTIONS = ['create', 'read', 'update', 'delete', 'manage']

def seed_permissions():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Seeding permissions...")
    
    count = 0
    for module in MODULES:
        for action in ACTIONS:
            perm_name = f"{module}.{action}"
            display_name = f"{module.replace('_', ' ').title()} {action.title()}"
            description = f"Can {action} {module.replace('_', ' ')}"
            
            try:
                # Check if exists
                cursor.execute("SELECT id FROM permissions WHERE name = ?", (perm_name,))
                if cursor.fetchone():
                    continue

                cursor.execute("""
                    INSERT INTO permissions (name, display_name, description, module, action, resource, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """, (perm_name, display_name, description, module, action, module, datetime.datetime.now()))
                count += 1
            except Exception as e:
                print(f"Error inserting {perm_name}: {e}")

    conn.commit()
    print(f"Added {count} new permissions.")
    conn.close()

if __name__ == "__main__":
    seed_permissions()
