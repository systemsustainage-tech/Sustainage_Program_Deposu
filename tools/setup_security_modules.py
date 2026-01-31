#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Güvenlik Modülleri Kurulum Scripti
SUSTAINAGE-SDG güvenlik özelliklerini mevcut sisteme entegre eder
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def install_requirements() -> None:
    """Gerekli kütüphaneleri yükle"""
    logging.info(" Gerekli kütüphaneler yükleniyor...")
    
    requirements_file = Path(__file__).parent.parent / "yonetim" / "requirements_security.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        logging.info(" Kütüphaneler başarıyla yüklendi!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f" Kütüphane yükleme hatası: {e}")
        return False

def create_security_tables() -> None:
    """Güvenlik tablolarını oluştur"""
    logging.info("️ Güvenlik tabloları oluşturuluyor...")
    
    # Veritabanı yolu
    db_path = Path(__file__).parent.parent / "data" / "sdg_desktop.sqlite"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Güvenlik audit tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_audit_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                username TEXT,
                event TEXT NOT NULL,
                ok INTEGER,
                meta TEXT
            )
        """)
        
        # Güvenlik audit log tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                actor TEXT,
                action TEXT,
                details TEXT
            )
        """)
        
        # System settings tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings(
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Password resets tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0
            )
        """)
        
        # Users tablosuna 2FA alanları ekle
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT")
        except sqlite3.OperationalError as e:
            logging.error(f'Silent error in setup_security_modules.py: {str(e)}')  # Alan zaten var
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN totp_enabled INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            logging.error(f'Silent error in setup_security_modules.py: {str(e)}')  # Alan zaten var
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN backup_codes TEXT")
        except sqlite3.OperationalError as e:
            logging.error(f'Silent error in setup_security_modules.py: {str(e)}')  # Alan zaten var
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            logging.error(f'Silent error in setup_security_modules.py: {str(e)}')  # Alan zaten var
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN deleted_at INTEGER")
        except sqlite3.OperationalError as e:
            logging.error(f'Silent error in setup_security_modules.py: {str(e)}')  # Alan zaten var
        
        conn.commit()
        conn.close()
        
        logging.info(" Güvenlik tabloları başarıyla oluşturuldu!")
        return True
        
    except Exception as e:
        logging.error(f" Tablo oluşturma hatası: {e}")
        return False

def create_directory_structure() -> None:
    """Dizin yapısını oluştur"""
    logging.info(" Dizin yapısı oluşturuluyor...")
    
    base_path = Path(__file__).parent.parent / "yonetim"
    
    directories = [
        "security/core",
        "security/gui", 
        "licensing/core",
        "licensing/gui",
        "licensing/tools",
        "licensing/keys"
    ]
    
    try:
        for directory in directories:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logging.info(" Dizin yapısı başarıyla oluşturuldu!")
        return True
        
    except Exception as e:
        logging.error(f" Dizin oluşturma hatası: {e}")
        return False

def create_init_files() -> None:
    """__init__.py dosyalarını oluştur"""
    logging.info(" Python paket dosyaları oluşturuluyor...")
    
    base_path = Path(__file__).parent.parent / "yonetim"
    
    init_files = [
        "security/__init__.py",
        "security/core/__init__.py",
        "security/gui/__init__.py",
        "licensing/__init__.py",
        "licensing/core/__init__.py",
        "licensing/gui/__init__.py",
        "licensing/tools/__init__.py"
    ]
    
    try:
        for init_file in init_files:
            file_path = base_path / init_file
            if not file_path.exists():
                file_path.write_text('# -*- coding: utf-8 -*-', encoding='utf-8')
        
        logging.info(" Python paket dosyaları başarıyla oluşturuldu!")
        return True
        
    except Exception as e:
        logging.error(f" Paket dosyası oluşturma hatası: {e}")
        return False

def test_imports() -> None:
    """Modül importlarını test et"""
    logging.info(" Modül importları test ediliyor...")
    
    try:
        # Güvenlik modüllerini test et
        sys.path.append(str(Path(__file__).parent.parent))
        
        from yonetim.security.core.auth import generate_totp_secret
        from yonetim.security.core.crypto import hash_password, verify_password
        from yonetim.security.core.hw import get_hwid_info

        # Test işlemleri
        test_password = "test123"
        hashed = hash_password(test_password)
        verified = verify_password(hashed, test_password)
        
        if verified:
            logging.info(" Şifre hash'leme testi başarılı!")
        else:
            logging.info(" Şifre hash'leme testi başarısız!")
            return False
        
        # TOTP test
        secret = generate_totp_secret()
        if secret:
            logging.info(" TOTP secret üretimi başarılı!")
        else:
            logging.info(" TOTP secret üretimi başarısız!")
            return False
        
        # Hardware ID test
        hw_info = get_hwid_info()
        if hw_info.get('hwid_core'):
            logging.info(" Donanım ID tespiti başarılı!")
        else:
            logging.info(" Donanım ID tespiti başarısız!")
            return False
        
        logging.info(" Tüm modül testleri başarılı!")
        return True
        
    except Exception as e:
        logging.error(f" Modül test hatası: {e}")
        return False

def main() -> None:
    """Ana kurulum fonksiyonu"""
    logging.info(" SUSTAINAGE-SDG Güvenlik Modülleri Kurulumu Başlıyor...")
    logging.info("=" * 60)
    
    steps = [
        ("Kütüphaneleri yükle", install_requirements),
        ("Dizin yapısını oluştur", create_directory_structure),
        ("Paket dosyalarını oluştur", create_init_files),
        ("Güvenlik tablolarını oluştur", create_security_tables),
        ("Modül testlerini çalıştır", test_imports)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        logging.info(f"\n {step_name}...")
        if step_func():
            success_count += 1
        else:
            logging.info(f" {step_name} başarısız!")
            break
    
    logging.info("\n" + "=" * 60)
    if success_count == len(steps):
        logging.info(" Tüm kurulum adımları başarıyla tamamlandı!")
        logging.info("\n Sonraki adımlar:")
        logging.info("1. Uygulamayı yeniden başlatın")
        logging.info("2. Yönetim panelinden 'Güvenlik' sekmesini kontrol edin")
        logging.info("3. Yönetim panelinden 'Lisanslama' sekmesini kontrol edin")
        logging.info("4. Gerekirse lisans anahtarı oluşturun")
    else:
        logging.info(f" Kurulum başarısız! ({success_count}/{len(steps)} adım tamamlandı)")
        logging.info("\n Sorun giderme:")
        logging.info("1. Python versiyonunuzu kontrol edin (3.8+)")
        logging.info("2. pip'in güncel olduğundan emin olun")
        logging.info("3. İnternet bağlantınızı kontrol edin")
        logging.error("4. Hata mesajlarını dikkatlice okuyun")

if __name__ == "__main__":
    main()
