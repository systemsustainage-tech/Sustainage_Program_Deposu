import sqlite3
import ftplib
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load environment variables
load_dotenv()

FTP_HOST = os.getenv('FTP_HOST', '72.62.150.207')
FTP_USER = os.getenv('FTP_USER', 'cursorsustainageftp')
FTP_PASS = os.getenv('FTP_PASS', 'Kayra_1507_Sk!')

LOCAL_DB_PATH = 'temp_remote_db.sqlite'

def main():
    try:
        print(f"Connecting to FTP {FTP_HOST}...")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")

        remote_path = '/httpdocs/backend/data/sdg_desktop.sqlite'
        
        print(f"Downloading {remote_path}...")
        with open(LOCAL_DB_PATH, 'wb') as f:
            ftp.retrbinary(f"RETR {remote_path}", f.write)
        print("Download complete.")
        
        ftp.quit()

        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check waste_generation
        print("\n--- waste_generation ---")
        try:
            cursor.execute("SELECT * FROM waste_generation")
            rows = cursor.fetchall()
            if not rows:
                print("Table exists but is empty.")
            else:
                for row in rows:
                    print(dict(row))
        except Exception as e:
            print(f"Error: {e}")

        # Check waste_recycling
        print("\n--- waste_recycling ---")
        try:
            cursor.execute("SELECT * FROM waste_recycling")
            rows = cursor.fetchall()
            if not rows:
                print("Table exists but is empty.")
            else:
                for row in rows:
                    print(dict(row))
        except Exception as e:
            print(f"Error: {e}")

        # Check companies
        print("\n--- companies ---")
        try:
            cursor.execute("SELECT id, name FROM companies")
            rows = cursor.fetchall()
            for row in rows:
                print(dict(row))
        except Exception as e:
            print(f"Error: {e}")

        # Check users
        print("\n--- users ---")
        try:
            # Check if company_id column exists in users (it might not, handled via user_manager logic)
            cursor.execute("PRAGMA table_info(users)")
            cols = [c[1] for c in cursor.fetchall()]
            print(f"Users columns: {cols}")
            
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                # Print select fields to avoid clutter
                r = dict(row)
                print(f"User: {r.get('username')}, Role: {r.get('role')}, CompanyID: {r.get('company_id')}")
        except Exception as e:
            print(f"Error: {e}")

        conn.close()
        
        # Clean up
        if os.path.exists(LOCAL_DB_PATH):
            os.remove(LOCAL_DB_PATH)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
