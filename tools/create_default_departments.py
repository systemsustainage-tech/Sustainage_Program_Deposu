#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standart Departmanlar Oluşturma
8 temel departmanı ve örnek kullanıcıları oluşturur.
"""

import logging
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#  GÜVENLİK: hashlib kaldırıldı, Argon2 kullanılıyor

# 8 Standart departman
DEPARTMENTS = [
    {
        'name': 'İnsan Kaynakları',
        'code': 'HR',
        'description': 'İstihdam, eğitim, sağlık ve çalışan verileri',
        'responsible_for': ['SDG 3', 'SDG 4', 'SDG 5', 'SDG 8', 'SDG 10']
    },
    {
        'name': 'Üretim',
        'code': 'PROD',
        'description': 'Enerji, su, atık ve üretim verileri',
        'responsible_for': ['SDG 6', 'SDG 7', 'SDG 9', 'SDG 12']
    },
    {
        'name': 'ÇSG',
        'code': 'EHS',
        'description': 'Çevre, Sağlık, Güvenlik - İklim ve emisyon verileri',
        'responsible_for': ['SDG 13', 'SDG 14', 'SDG 15']
    },
    {
        'name': 'Satınalma',
        'code': 'PROC',
        'description': 'Tedarikçi, yerel tedarik ve satınalma verileri',
        'responsible_for': ['SDG 12']
    },
    {
        'name': 'Finans',
        'code': 'FIN',
        'description': 'Ekonomik performans ve yatırım verileri',
        'responsible_for': ['SDG 8', 'SDG 17']
    },
    {
        'name': 'Kalite',
        'code': 'QA',
        'description': 'Kalite yönetimi ve müşteri memnuniyeti',
        'responsible_for': ['SDG 9', 'SDG 12']
    },
    {
        'name': 'Ar-Ge',
        'code': 'RD',
        'description': 'Araştırma, geliştirme ve inovasyon',
        'responsible_for': ['SDG 9']
    },
    {
        'name': 'Sosyal Sorumluluk',
        'code': 'CSR',
        'description': 'Toplumsal projeler, bağışlar ve sosyal faaliyetler',
        'responsible_for': ['SDG 1', 'SDG 2', 'SDG 11', 'SDG 16', 'SDG 17']
    },
]

# Her departman için örnek kullanıcı
SAMPLE_USERS = [
    {'username': 'hr_user', 'name': 'İK Sorumlusu', 'dept': 'İnsan Kaynakları', 'email': 'ik@company.com'},
    {'username': 'prod_user', 'name': 'Üretim Sorumlusu', 'dept': 'Üretim', 'email': 'uretim@company.com'},
    {'username': 'ehs_user', 'name': 'ÇSG Sorumlusu', 'dept': 'ÇSG', 'email': 'csg@company.com'},
    {'username': 'proc_user', 'name': 'Satınalma Sorumlusu', 'dept': 'Satınalma', 'email': 'satin@company.com'},
    {'username': 'fin_user', 'name': 'Finans Sorumlusu', 'dept': 'Finans', 'email': 'finans@company.com'},
    {'username': 'qa_user', 'name': 'Kalite Sorumlusu', 'dept': 'Kalite', 'email': 'kalite@company.com'},
    {'username': 'rd_user', 'name': 'Ar-Ge Sorumlusu', 'dept': 'Ar-Ge', 'email': 'arge@company.com'},
    {'username': 'csr_user', 'name': 'Sosyal Sorumluluk Sorumlusu', 'dept': 'Sosyal Sorumluluk', 'email': 'ssr@company.com'},
]

def create_departments() -> None:
    """8 standart departmanı oluştur"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    logging.info("=" * 60)
    logging.info("STANDART DEPARTMANLAR OLUŞTURULUYOR")
    logging.info("=" * 60)
    
    try:
        # Departments tablosu var mı kontrol et
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                code TEXT UNIQUE,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("\n[OK] departments tablosu hazır\n")
        
        # Departmanları oluştur
        dept_ids = {}
        
        for i, dept in enumerate(DEPARTMENTS, 1):
            try:
                # Önce var mı kontrol et
                cursor.execute("SELECT id FROM departments WHERE name = ?", (dept['name'],))
                existing = cursor.fetchone()
                
                if existing:
                    dept_id = existing[0]
                else:
                    # Yoksa oluştur (company_id=1 varsayılan)
                    cursor.execute("""
                        INSERT INTO departments (name, code, description, company_id)
                        VALUES (?, ?, ?, 1)
                    """, (dept['name'], dept['code'], dept['description']))
                    dept_id = cursor.lastrowid
                
                dept_ids[dept['name']] = dept_id
                
                logging.info(f"[{i}/8] {dept['name']} (ID: {dept_id})")
                logging.info(f"      Kod: {dept['code']}")
                logging.info(f"      Sorumlu: {', '.join(dept['responsible_for'])}")
                
            except Exception as e:
                logging.error(f"[HATA] {dept['name']}: {e}")
        
        conn.commit()
        
        logging.info("\n" + "=" * 60)
        logging.info("[BAŞARILI] 8 standart departman oluşturuldu!")
        logging.info("=" * 60)
        
        return dept_ids
        
    except Exception as e:
        logging.error(f"\n[HATA] Departman oluşturma hatası: {e}")
        conn.rollback()
        return {}
        
    finally:
        conn.close()

def create_sample_users(dept_ids) -> None:
    """Her departman için örnek kullanıcı oluştur"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    logging.info("\n" + "=" * 60)
    logging.info("ÖRNEK KULLANICILAR OLUŞTURULUYOR")
    logging.info("=" * 60 + "\n")
    
    try:
        # Varsayılan şifre: "user123"
        #  GÜVENLİK: Argon2 kullanılıyor
        from yonetim.security.core.crypto import hash_password
        default_password = "user123"
        password_hash = hash_password(default_password)
        
        for i, user in enumerate(SAMPLE_USERS, 1):
            dept_id = dept_ids.get(user['dept'])
            
            if not dept_id:
                logging.info(f"[UYARI] {user['name']} - Departman bulunamadı: {user['dept']}")
                continue
            
            try:
                # Kullanıcı zaten var mı kontrol et
                cursor.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Varsa departman bilgisini güncelle
                    cursor.execute("""
                        UPDATE users 
                        SET department = ?,
                            display_name = ?,
                            email = ?
                        WHERE username = ?
                    """, (user['dept'], user['name'], user['email'], user['username']))
                    logging.info(f"[{i}/8] {user['name']} - Güncellendi (departman: {user['dept']})")
                else:
                    # Yoksa oluştur
                    cursor.execute("""
                        INSERT INTO users (username, display_name, email, password_hash, department, role, is_active)
                        VALUES (?, ?, ?, ?, ?, 'user', 1)
                    """, (user['username'], user['name'], user['email'], password_hash, user['dept']))
                    logging.info(f"[{i}/8] {user['name']} - Oluşturuldu (departman: {user['dept']})")
                    logging.info(f"      Kullanıcı adı: {user['username']}")
                    logging.info(f"      Şifre: {default_password}")
                
            except Exception as e:
                logging.error(f"[HATA] {user['name']}: {e}")
        
        conn.commit()
        
        logging.info("\n" + "=" * 60)
        logging.info("[BAŞARILI] Örnek kullanıcılar oluşturuldu!")
        logging.info("=" * 60)
        logging.info("\nVarsayılan şifre: user123")
        logging.info("Kullanıcılar:")
        for user in SAMPLE_USERS:
            logging.info(f"  - {user['username']} ({user['dept']})")
        
        return True
        
    except Exception as e:
        logging.error(f"\n[HATA] Kullanıcı oluşturma hatası: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main() -> None:
    """Ana fonksiyon"""
    logging.info("\nSTANDART DEPARTMANLAR VE KULLANICILAR KURULUMU\n")
    
    # 1. Departmanları oluştur
    dept_ids = create_departments()
    
    if not dept_ids:
        logging.error("\n[HATA] Departmanlar oluşturulamadı!")
        return
    
    # 2. Örnek kullanıcıları oluştur
    success = create_sample_users(dept_ids)
    
    if success:
        logging.info("\n[BASARILI] Kurulum tamamlandi!")
        logging.info("\nSimdi yapabilecekleriniz:")
        logging.info("  1. Kullanicilarla giris yapin (sifre: user123)")
        logging.info("  2. Yonetim -> Kullanici Yonetimi'nden duzenleyin")
        logging.info("  3. SDG hedefi secince otomatik departmanlara gorev gider")
    else:
        logging.error("\n[HATA] Kurulum başarısız!")

if __name__ == "__main__":
    main()

