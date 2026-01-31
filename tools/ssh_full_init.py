
import paramiko
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

# Embedded Remote Script
REMOTE_SCRIPT = """
import os
import sys
import sqlite3
import logging
import subprocess

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants
DB_DIR = '/var/www/sustainage/backend/data'
DB_PATH = os.path.join(DB_DIR, 'sdg_desktop.sqlite')
LOG_DIR = '/var/www/sustainage/logs'

def install_dependencies():
    logging.info("Installing dependencies...")
    pkgs = ["flask", "flask-session", "werkzeug", "pandas", "matplotlib", "openpyxl", "requests", "argon2-cffi"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + pkgs + ["--break-system-packages"])
        logging.info("Dependencies installed.")
    except Exception as e:
        logging.error(f"Dependency install failed: {e}")
        # Proceeding anyway as they might be installed via apt or other means

def setup_directories():
    logging.info("Setting up directories...")
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    # Set permissions (will be refined later)
    os.chmod(DB_DIR, 0o775)
    os.chmod(LOG_DIR, 0o775)

def init_database():
    logging.info(f"Initializing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Users Schema
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20),
        department VARCHAR(100),
        position VARCHAR(100),
        avatar_path VARCHAR(255),
        is_active BOOLEAN DEFAULT 1,
        is_verified BOOLEAN DEFAULT 0,
        last_login TIMESTAMP,
        login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        updated_by INTEGER
    );

    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL UNIQUE,
        display_name VARCHAR(100) NOT NULL,
        description TEXT,
        is_system_role BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, role_id)
    );
    ''')
    
    # 2. Modules Schema
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_code TEXT UNIQUE NOT NULL,
        module_name TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        category TEXT,
        display_order INTEGER,
        is_core INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        route TEXT
    );
    ''')
    
    # 3. Insert Default Roles
    roles = [
        ('super_admin', 'Süper Yönetici', 'Sistem tam kontrolü', 1),
        ('admin', 'Yönetici', 'Sistem yönetimi', 0),
        ('user', 'Kullanıcı', 'Standart kullanıcı', 0)
    ]
    for r in roles:
        cursor.execute("INSERT OR IGNORE INTO roles (name, display_name, description, is_system_role) VALUES (?, ?, ?, ?)", r)
        
    # 4. Insert Modules (19 Modules)
    modules = [
        ('carbon', 'Karbon Ayak İzi', 'Karbon emisyon hesaplama', 'co2', 'env', 1, 1, 1, '/modules/carbon'),
        ('water', 'Su Ayak İzi', 'Su tüketim takibi', 'water_drop', 'env', 2, 1, 1, '/modules/water'),
        ('waste', 'Atık Yönetimi', 'Atık takibi', 'delete', 'env', 3, 1, 1, '/modules/waste'),
        ('energy', 'Enerji Yönetimi', 'Enerji tüketim analizi', 'bolt', 'env', 4, 1, 1, '/modules/energy'),
        ('social', 'Sosyal Etki', 'Sosyal sorumluluk projeleri', 'groups', 'soc', 5, 0, 1, '/modules/social'),
        ('governance', 'Kurumsal Yönetişim', 'Yönetim süreçleri', 'gavel', 'gov', 6, 0, 1, '/modules/governance'),
        ('supply_chain', 'Tedarik Zinciri', 'Tedarikçi denetimi', 'local_shipping', 'gov', 7, 0, 1, '/modules/supply_chain'),
        ('human_rights', 'İnsan Hakları', 'İnsan hakları uyumu', 'accessibility', 'soc', 8, 0, 1, '/modules/human_rights'),
        ('labor', 'Çalışma Standartları', 'İşçi hakları', 'work', 'soc', 9, 0, 1, '/modules/labor'),
        ('ethics', 'İş Etiği', 'Etik kurallar', 'policy', 'gov', 10, 0, 1, '/modules/ethics'),
        ('biodiversity', 'Biyoçeşitlilik', 'Doğal yaşamı koruma', 'forest', 'env', 11, 0, 1, '/modules/biodiversity'),
        ('product_responsibility', 'Ürün Sorumluluğu', 'Ürün güvenliği', 'verified', 'gov', 12, 0, 1, '/modules/product'),
        ('community', 'Topluluk İlişkileri', 'Yerel halk ile ilişkiler', 'handshake', 'soc', 13, 0, 1, '/modules/community'),
        ('economic', 'Ekonomik Performans', 'Finansal sürdürülebilirlik', 'trending_up', 'gov', 14, 0, 1, '/modules/economic'),
        ('climate_risk', 'İklim Riski', 'İklim değişikliği riskleri', 'thermostat', 'env', 15, 0, 1, '/modules/climate'),
        ('innovation', 'İnovasyon', 'Ar-Ge ve yenilikçilik', 'lightbulb', 'gov', 16, 0, 1, '/modules/innovation'),
        ('training', 'Eğitim', 'Çalışan eğitimleri', 'school', 'soc', 17, 0, 1, '/modules/training'),
        ('health_safety', 'İş Sağlığı ve Güvenliği', 'İSG uygulamaları', 'health_and_safety', 'soc', 18, 0, 1, '/modules/health'),
        ('audit', 'Denetim', 'İç ve dış denetimler', 'fact_check', 'gov', 19, 0, 1, '/modules/audit')
    ]
    for m in modules:
        cursor.execute("INSERT OR IGNORE INTO modules (module_code, module_name, description, icon, category, display_order, is_core, is_active, route) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", m)
        
    conn.commit()
    return conn

def create_super_user(conn):
    logging.info("Creating Super User...")
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        password_hash = ph.hash("super123")
    except ImportError:
        logging.warning("argon2-cffi not found, using placeholder hash (LOGIN MIGHT FAIL)")
        password_hash = "placeholder"
    except Exception as e:
        logging.error(f"Hashing failed: {e}")
        password_hash = "error"

    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM users WHERE username='__super__'")
    if cursor.fetchone():
        logging.info("Super user already exists. Updating password...")
        cursor.execute("UPDATE users SET password_hash=? WHERE username='__super__'", (password_hash,))
    else:
        logging.info("Creating new super user...")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_verified)
            VALUES (?, ?, ?, ?, ?, 1, 1)
        ''', ('__super__', 'super@sustainage.cloud', password_hash, 'Super', 'Admin'))
    
    # Assign Role
    user_id = cursor.execute("SELECT id FROM users WHERE username='__super__'").fetchone()[0]
    role_id = cursor.execute("SELECT id FROM roles WHERE name='super_admin'").fetchone()[0]
    cursor.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
    
    conn.commit()
    logging.info("Super user setup complete.")

def main():
    install_dependencies()
    setup_directories()
    conn = init_database()
    create_super_user(conn)
    conn.close()
    
    # Final Permissions
    subprocess.call(["chown", "-R", "www-data:www-data", "/var/www/sustainage"])
    logging.info("Full initialization complete.")

if __name__ == "__main__":
    main()
"""

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        # Upload Script
        sftp = client.open_sftp()
        with sftp.file('/var/www/sustainage/full_init.py', 'w') as f:
            f.write(REMOTE_SCRIPT)
        
        # Run Script
        logging.info("Running initialization script on server...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/full_init.py")
        
        # Stream output
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())
            
        err = stderr.read().decode()
        if err:
            logging.error(f"Errors:\n{err}")
            
        client.exec_command("rm /var/www/sustainage/full_init.py")
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
