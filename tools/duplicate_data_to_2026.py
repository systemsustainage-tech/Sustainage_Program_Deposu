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

LOCAL_DB_PATH = 'temp_update_year.sqlite'

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
        
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        tables_to_update = [
            'waste_generation', 'waste_recycling', 
            'carbon_emissions', 'energy_consumption', 'water_consumption'
        ]

        for table in tables_to_update:
            print(f"\nProcessing {table}...")
            try:
                # Check columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [c[1] for c in cursor.fetchall()]
                
                has_year = 'year' in columns
                has_period = 'period' in columns
                
                if not has_year and not has_period:
                    print(f"Skipping {table}: No year or period column.")
                    continue
                
                # Construct SELECT query excluding 'id' and 'created_at'
                cols_to_select = [c for c in columns if c not in ['id', 'created_at']]
                cols_str = ", ".join(cols_to_select)
                
                # Check if there is data for 2025
                if has_year:
                    cursor.execute(f"SELECT {cols_str} FROM {table} WHERE year = 2025")
                else:
                    cursor.execute(f"SELECT {cols_str} FROM {table} WHERE period LIKE '2025%'")
                    
                rows = cursor.fetchall()
                if not rows:
                    print(f"No 2025 data found in {table}.")
                    # If no 2025 data, maybe try to insert sample data for 2026?
                    # But for now, let's just duplicate if exists.
                    continue
                
                print(f"Found {len(rows)} rows for 2025 in {table}. Duplicating for 2026...")
                
                for row in rows:
                    data = dict(zip(cols_to_select, row))
                    
                    if has_year:
                        data['year'] = 2026
                    
                    if has_period:
                        if '2025' in str(data['period']):
                            data['period'] = str(data['period']).replace('2025', '2026')
                        else:
                            # If period is not year-based (unlikely), set it to 2026
                            data['period'] = '2026'
                    
                    placeholders = ", ".join(["?" for _ in cols_to_select])
                    values = [data[c] for c in cols_to_select]
                    
                    cursor.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})", values)
                    
                print(f"Duplicated {len(rows)} rows into 2026.")
                
            except Exception as e:
                print(f"Error processing {table}: {e}")

        conn.commit()
        conn.close()
        print("\nDatabase updated locally.")

        print(f"Uploading updated DB to {remote_path}...")
        with open(LOCAL_DB_PATH, 'rb') as f:
            ftp.storbinary(f"STOR {remote_path}", f)
        print("Upload complete.")
        
        ftp.quit()
        
        # Clean up
        if os.path.exists(LOCAL_DB_PATH):
            os.remove(LOCAL_DB_PATH)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
