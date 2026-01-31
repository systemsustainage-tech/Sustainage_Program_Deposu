"""
Modules tablosunu duzelten script (Correct Schema)
"""

import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_modules_table() -> None:
    """Modules tablosunu yeniden olustur"""
    
    # Correct DB Path: c:/SDG/server/backend/data/sdg_desktop.sqlite
    # Assuming this script is in c:/SDG/tools/
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'backend', 'data', 'sdg_desktop.sqlite'))
    
    logging.info(f"Veritabani: {db_path}")
    
    if not os.path.exists(db_path):
        logging.error("Veritabani dosyasi bulunamadi!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eski modules tablosunu yedekle
        logging.info("1. Eski modules tablosu yedekleniyor...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='modules'")
        if cursor.fetchone():
            cursor.execute('DROP TABLE IF EXISTS modules_backup')
            cursor.execute('CREATE TABLE modules_backup AS SELECT * FROM modules')
        
        # Eski tabloyu sil
        logging.info("2. Eski modules tablosu siliniyor...")
        cursor.execute('DROP TABLE IF EXISTS modules')
        
        # Yeni modules tablosunu olustur (Correct Schema)
        logging.info("3. Yeni modules tablosu olusturuluyor...")
        cursor.execute('''
            CREATE TABLE modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT UNIQUE NOT NULL,
                module_name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                category TEXT,
                display_order INTEGER,
                is_core INTEGER DEFAULT 0,
                default_enabled INTEGER DEFAULT 1
            )
        ''')
        
        # Modulleri ekle
        logging.info("4. Moduller ekleniyor...")
        modules_data = [
            # Environmental
            ('carbon', 'Karbon Ayak İzi', 'Karbon emisyon hesaplama', 'co2', 'Environmental', 10, 1, 1),
            ('energy', 'Enerji Yönetimi', 'Enerji tüketimi ve verimlilik', 'bolt', 'Environmental', 11, 1, 1),
            ('water', 'Su Yönetimi', 'Su tüketimi ve geri kazanım', 'water_drop', 'Environmental', 12, 1, 1),
            ('waste', 'Atık Yönetimi', 'Atık takibi ve geri dönüşüm', 'recycling', 'Environmental', 13, 1, 1),
            ('biodiversity', 'Biyoçeşitlilik', 'Biyoçeşitlilik ve ekosistem', 'forest', 'Environmental', 14, 0, 1),
            ('cbam', 'SKDM (CBAM)', 'Sınırda Karbon Düzenleme', 'public', 'Environmental', 15, 0, 1),
            ('eu_taxonomy', 'AB Taksonomisi', 'Sürdürülebilir finans taksonomisi', 'euro', 'Environmental', 16, 0, 1),
            
            # Social & Governance
            ('social', 'Sosyal Etki', 'İnsan hakları ve sosyal etki', 'groups', 'Social', 20, 1, 1),
            ('ohs', 'İSG', 'İş sağlığı ve güvenliği', 'health_and_safety', 'Social', 21, 1, 1),
            ('supply_chain', 'Tedarik Zinciri', 'Tedarikçi sürdürülebilirliği', 'local_shipping', 'Social', 22, 0, 1),
            ('governance', 'Kurumsal Yönetişim', 'Yönetim kurulu ve politikalar', 'gavel', 'Governance', 23, 1, 1),
            ('stakeholder', 'Paydaş Katılımı', 'Paydaş analizi ve geri bildirim', 'handshake', 'Governance', 24, 0, 1),
            
            # Frameworks
            ('sdg', 'SDG', 'Sürdürülebilir Kalkınma Hedefleri', 'sdg', 'Frameworks', 30, 1, 1),
            ('gri', 'GRI', 'Global Reporting Initiative', 'gri', 'Frameworks', 31, 1, 1),
            ('esrs', 'ESRS', 'Avrupa Sürdürülebilirlik Raporlama', 'description', 'Frameworks', 32, 0, 1),
            ('sasb', 'SASB', 'Sektörel standartlar', 'business', 'Frameworks', 33, 0, 1),
            ('ifrs', 'IFRS (ISSB)', 'Uluslararası Finansal Raporlama', 'account_balance', 'Frameworks', 34, 0, 1),
            ('tcfd', 'TCFD', 'İklimle ilgili finansal beyanlar', 'thermostat', 'Frameworks', 35, 0, 1),
            ('tnfd', 'TNFD', 'Doğa ile ilgili finansal beyanlar', 'nature', 'Frameworks', 36, 0, 1),
            ('cdp', 'CDP', 'Carbon Disclosure Project', 'cloud', 'Frameworks', 37, 0, 1),
            
            # Core
            ('reports', 'Raporlar', 'Raporlama merkezi', 'assessment', 'Core', 90, 1, 1),
            ('management', 'Ayarlar', 'Sistem ayarları', 'settings', 'Core', 99, 1, 1),
        ]
        
        for m in modules_data:
            try:
                cursor.execute('''
                    INSERT INTO modules (module_code, module_name, description, icon, category, display_order, is_core, default_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', m)
                logging.info(f"  + {m[1]} ({m[0]})")
            except sqlite3.IntegrityError:
                logging.warning(f"  ! {m[1]} zaten var (atlandı)")
        
        # Company_modules tablosunu da kontrol et (Yeniden olustur)
        logging.info("5. company_modules tablosu yeniden olusturuluyor...")
        cursor.execute('DROP TABLE IF EXISTS company_modules')
        
        cursor.execute('''
            CREATE TABLE company_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                FOREIGN KEY (module_id) REFERENCES modules (id)
            )
        ''')
        
        # Populate company_modules for existing companies
        cursor.execute("SELECT id FROM companies")
        companies = cursor.fetchall()
        cursor.execute("SELECT id FROM modules")
        module_ids = cursor.fetchall()
        
        for company in companies:
            c_id = company[0]
            for m_id in module_ids:
                cursor.execute("INSERT INTO company_modules (company_id, module_id, is_enabled) VALUES (?, ?, 1)", (c_id, m_id[0]))
        
        conn.commit()
        logging.info("\nBasarili! Modules tablosu duzeltildi.")
        
        conn.close()
        
    except Exception as e:
        logging.error(f"\nHata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_modules_table()
