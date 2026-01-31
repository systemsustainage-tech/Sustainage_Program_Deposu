import sqlite3
import os

# Correct DB Path based on remote_schema_fix_columns.py
DB_PATH = "/var/www/sustainage/data/sdg_desktop.sqlite"

def inspect_tables():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"--- Inspecting DB at {DB_PATH} ---")
    
    # Check tables
    print("\n--- Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    for t in tables:
        print(f"- {t}")
    
    # Check companies table columns
    if 'companies' in tables:
        print("\n--- Columns in 'companies' ---")
        cursor.execute("PRAGMA table_info(companies)")
        for col in cursor.fetchall():
            print(f"{col['cid']}: {col['name']} ({col['type']})")
            
    # Check user_companies table columns
    if 'user_companies' in tables:
        print("\n--- Columns in 'user_companies' ---")
        cursor.execute("PRAGMA table_info(user_companies)")
        for col in cursor.fetchall():
            print(f"{col['cid']}: {col['name']} ({col['type']})")
    else:
        print("\n! 'user_companies' table NOT FOUND")

    # Check Social tables
    social_tables = ['hr_employees', 'ohs_incidents', 'training_records']
    for t in social_tables:
        if t in tables:
            print(f"\n--- Columns in '{t}' ---")
            cursor.execute(f"PRAGMA table_info({t})")
            for col in cursor.fetchall():
                print(f"{col['cid']}: {col['name']} ({col['type']})")

    # Check Governance & Economic tables (Existing candidates)
    gov_eco_tables = [
        'governance_structure', 'board_members', 'governance_committees',
        'economic_value_distribution', 'tax_contributions'
    ]
    for t in gov_eco_tables:
        if t in tables:
            print(f"\n--- Columns in '{t}' ---")
            cursor.execute(f"PRAGMA table_info({t})")
            for col in cursor.fetchall():
                print(f"{col['cid']}: {col['name']} ({col['type']})")
        else:
            print(f"\n! Table '{t}' NOT FOUND")


    # Check content of companies
    if 'companies' in tables:
        print("\n--- Content of 'companies' (first 5) ---")
        cursor.execute("SELECT * FROM companies LIMIT 5")
        for row in cursor.fetchall():
            print(dict(row))

    # Check content of user_companies
    if 'user_companies' in tables:
        print("\n--- Content of 'user_companies' (first 5) ---")
        cursor.execute("SELECT * FROM user_companies LIMIT 5")
        for row in cursor.fetchall():
            print(dict(row))

    conn.close()

if __name__ == "__main__":
    inspect_tables()
