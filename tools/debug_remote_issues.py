
import sqlite3
import os

def check_sdg():
    print("\n--- SDG Check ---")
    db_path = "/var/www/sustainage/data/sdg_desktop.sqlite"
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables found: {len(tables)}")
        if 'users' not in tables:
            print("WARNING: 'users' table missing!")
        if 'companies' not in tables:
            print("WARNING: 'companies' table missing!")

        # Check indicators
        cursor.execute("SELECT count(*) FROM sdg_indicators")
        count = cursor.fetchone()[0]
        print(f"sdg_indicators count: {count}")

        # Check companies
        cursor.execute("SELECT count(*) FROM companies")
        count = cursor.fetchone()[0]
        print(f"companies count: {count}")
        
        cursor.execute("SELECT id, name FROM companies LIMIT 5")
        rows = cursor.fetchall()
        print("Companies:")
        for r in rows:
            print(r)
        
        cursor.execute("SELECT id, title_tr FROM sdg_indicators WHERE id=1")
        row = cursor.fetchone()
        print(f"Indicator 1: {row}")
        
        # Check responses
        cursor.execute("SELECT * FROM responses ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        print(f"Last response: {row}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def check_cbam():
    print("\n--- CBAM Check ---")
    db_path = "/var/www/sustainage/data/sdg_desktop.sqlite"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check products
        cursor.execute("SELECT id, product_code, product_name, cn_code FROM cbam_products ORDER BY created_at DESC LIMIT 3")
        rows = cursor.fetchall()
        print("Recent Products:")
        for r in rows:
            print(r)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def check_csrd():
    print("\n--- CSRD Check ---")
    db_path = "/var/www/sustainage/data/sdg_desktop.sqlite"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check assessments
        cursor.execute("SELECT topic_code, topic_name FROM double_materiality_assessment ORDER BY created_at DESC LIMIT 3")
        rows = cursor.fetchall()
        print("Recent Assessments:")
        for r in rows:
            print(r)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sdg()
    check_cbam()
    check_csrd()
