import sqlite3
import os
import sys

# Add project root and backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DB_PATH

def fix_system_roles():
    print(f"Database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    system_roles = ['admin', 'manager', 'analyst', 'user', 'viewer']
    
    print(f"Updating roles to be system roles: {system_roles}")
    
    placeholders = ','.join(['?' for _ in system_roles])
    query = f"UPDATE roles SET is_system_role = 1 WHERE name IN ({placeholders})"
    
    cursor.execute(query, system_roles)
    print(f"Updated {cursor.rowcount} rows.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_system_roles()
