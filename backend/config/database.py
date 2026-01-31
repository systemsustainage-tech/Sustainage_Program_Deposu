# -*- coding: utf-8 -*-
import os

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Veritabanı yolu
if os.name == 'nt':
    # Windows (Local Development)
    DB_PATH = os.path.join(ROOT_DIR, 'data', 'sdg_desktop.sqlite')
else:
    # Linux (Remote Server)
    DB_PATH = '/var/www/sustainage/sustainage.db'

def get_db_path():
    """Veritabanı yolunu döndürür"""
    return DB_PATH
