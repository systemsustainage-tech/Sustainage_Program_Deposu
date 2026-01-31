import os
import datetime

def check_db_files():
    paths = [
        '/var/www/sustainage/sustainage.db',
        '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    ]
    
    for p in paths:
        if os.path.exists(p):
            stat = os.stat(p)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
            print(f"{p}: Size={stat.st_size} bytes, Modified={mtime}")
        else:
            print(f"{p}: Not found")

if __name__ == "__main__":
    check_db_files()
