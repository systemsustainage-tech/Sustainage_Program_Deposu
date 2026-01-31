import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if os.name == 'nt':
    DB_PATH = os.path.join(BACKEND_DIR, "data", "sdg_desktop.sqlite")
else:
    DB_PATH = '/var/www/sustainage/sustainage.db'

def get_db_path():
    return DB_PATH
