
import paramiko
import sqlite3

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_mapping_data():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        tables_to_check = ['map_sdg_gri', 'map_sdg_tsrs', 'map_sdg_esrs']
        
        for table in tables_to_check:
            cmd = f"sqlite3 {DB_PATH} \"SELECT COUNT(*) FROM {table};\""
            stdin, stdout, stderr = client.exec_command(cmd)
            err = stderr.read().decode()
            if "no such table" in err:
                print(f"{table}: MISSING")
            else:
                count = stdout.read().decode().strip()
                print(f"{table}: {count} rows")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_mapping_data()
