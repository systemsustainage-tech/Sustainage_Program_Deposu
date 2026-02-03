import sqlite3
import secrets
import datetime
import argparse
import os
import sys
import os

# Add backend directory to path to import database config if needed
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(BACKEND_DIR)

try:
    from yonetim.license_manager import LicenseManager
except ImportError:
    print("Error: Could not import LicenseManager. Ensure 'backend' directory is in python path.")
    sys.exit(1)

def get_db_connection(db_path=None):
    if not db_path:
        # Default paths
        if os.name == 'nt':
             db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
        else:
             db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        # sys.exit(1) # Don't exit here, let LicenseManager handle it or user provide path
    return db_path

def create_license(company_id, max_users=5, days=365, db_path=None):
    db_path = get_db_connection(db_path)
    
    # Verify company exists first (optional, but good UX)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies WHERE id = ?", (company_id,))
    company = cursor.fetchone()
    conn.close()
    
    if not company:
        print(f"Error: Company with ID {company_id} not found.")
        return

    lm = LicenseManager(db_path)
    result = lm.generate_license(company_id, duration_days=days, max_users=max_users)
    
    if result.get('success'):
        print(f"License created successfully for company '{company[1]}' (ID: {company_id}).")
        print(f"Key: {result['license_key']}")
        print(f"Expires: {result['expires_at']}")
    else:
        print(f"Error creating license: {result.get('message')}")

def list_licenses(db_path=None):
    db_path = get_db_connection(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT l.*, c.name as company_name 
        FROM licenses l 
        JOIN companies c ON l.company_id = c.id
        ORDER BY l.issued_at DESC
    """
    
    try:
        cursor.execute(query)
        licenses = cursor.fetchall()
        
        if not licenses:
            print("No licenses found.")
        else:
            print(f"{'ID':<5} {'Company':<20} {'Status':<10} {'Expires':<20} {'Key':<45}")
            print("-" * 100)
            for l in licenses:
                print(f"{l['id']:<5} {l['company_name']:<20} {l['status']:<10} {l['expires_at']:<20} {l['license_key']:<45}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:        
        conn.close()

def revoke_license(license_key, db_path=None):
    db_path = get_db_connection(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE licenses SET status = 'revoked' WHERE license_key = ?", (license_key,))
        if cursor.rowcount > 0:
            print("License revoked successfully.")
            conn.commit()
        else:
            print("License key not found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Sustainage Licenses")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new license')
    create_parser.add_argument('company_id', type=int, help='Company ID')
    create_parser.add_argument('--users', type=int, default=5, help='Max users')
    create_parser.add_argument('--days', type=int, default=365, help='Validity in days')
    create_parser.add_argument('--db', type=str, help='Path to database file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all licenses')
    list_parser.add_argument('--db', type=str, help='Path to database file')

    # Revoke command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke a license')
    revoke_parser.add_argument('key', type=str, help='License Key')
    revoke_parser.add_argument('--db', type=str, help='Path to database file')

    args = parser.parse_args()
    
    if args.command == 'create':
        create_license(args.company_id, args.users, args.days, args.db)
    elif args.command == 'list':
        list_licenses(args.db)
    elif args.command == 'revoke':
        revoke_license(args.key, args.db)
    else:
        parser.print_help()
