
import paramiko
import sys

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def update_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        # SQL commands
        sqls = [
            """
            CREATE TABLE IF NOT EXISTS carbon_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                period TEXT,
                scope TEXT,
                category TEXT,
                quantity REAL,
                unit TEXT,
                co2e_emissions REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS report_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                module_code TEXT,
                report_name TEXT,
                report_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                reporting_period TEXT,
                description TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        
        for sql in sqls:
            # Escape quotes for shell
            safe_sql = sql.replace('"', '\\"').replace('\n', ' ')
            cmd = f"python3 -c \"import sqlite3; conn = sqlite3.connect('/var/www/sustainage/backend/data/sdg_desktop.sqlite'); cursor = conn.cursor(); cursor.execute('{safe_sql}'); conn.commit(); conn.close()\""
            
            print(f"Executing SQL...")
            stdin, stdout, stderr = client.exec_command(cmd)
            err = stderr.read().decode()
            if err:
                print(f"Error: {err}")
            else:
                print("Success.")
                
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    update_schema()
