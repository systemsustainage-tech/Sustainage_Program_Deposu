"""
Database optimizasyon aracı
Index'ler ekler ve database performansını artırır
"""

import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def optimize_database() -> None:
    """Database'i optimize et - index'ler ekle"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sdg_desktop.sqlite')
    
    logging.info(f"Database optimize ediliyor: {db_path}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Index'leri oluştur
        indexes = [
            # Users tablosu
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            
            # User roles
            "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id)",
            
            # Role permissions
            "CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id)",
            "CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id)",
            
            # Companies
            "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)",
            
            # Company modules
            "CREATE INDEX IF NOT EXISTS idx_company_modules_company_id ON company_modules(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_company_modules_module_code ON company_modules(module_code)",
            
            # SDG data
            "CREATE INDEX IF NOT EXISTS idx_sdg_data_company_id ON sdg_data(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_sdg_data_goal_id ON sdg_data(goal_id)",
            "CREATE INDEX IF NOT EXISTS idx_sdg_data_date ON sdg_data(reporting_date)",
            
            # GRI data
            "CREATE INDEX IF NOT EXISTS idx_gri_data_company_id ON gri_data(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_gri_data_disclosure_id ON gri_data(disclosure_id)",
            
            # TSRS data
            "CREATE INDEX IF NOT EXISTS idx_tsrs_data_company_id ON tsrs_data(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_tsrs_data_standard_id ON tsrs_data(standard_id)",
            
            # Yeni modül tabloları
            "CREATE INDEX IF NOT EXISTS idx_innovation_company_year ON innovation_metrics(company_id, year)",
            "CREATE INDEX IF NOT EXISTS idx_quality_company_year ON quality_metrics(company_id, year)",
            "CREATE INDEX IF NOT EXISTS idx_digital_security_company_year ON digital_security_metrics(company_id, year)",
            "CREATE INDEX IF NOT EXISTS idx_emergency_company_year ON emergency_management_metrics(company_id, year)",
            
            # Audit log
            "CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(username)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action_type)",
        ]
        
        created_count = 0
        for idx_sql in indexes:
            try:
                cursor.execute(idx_sql)
                index_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ON")[0]
                logging.info(f"  + {index_name}")
                created_count += 1
            except Exception as e:
                logging.error(f"  ! Hata: {e}")
        
        conn.commit()
        
        logging.info(f"\n{created_count} index olusturuldu/kontrol edildi")
        
        # ANALYZE komutu - istatistikleri güncelle
        logging.info("\nDatabase istatistikleri guncelleniyor...")
        cursor.execute("ANALYZE")
        conn.commit()
        
        # VACUUM - database'i optimize et
        logging.info("Database optimize ediliyor (VACUUM)...")
        cursor.execute("VACUUM")
        
        logging.info("\nOptimizasyon tamamlandi!")
        
        # Performans raporu
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        total_indexes = cursor.fetchone()[0]
        logging.info(f"\nToplam index sayisi: {total_indexes}")
        
        # Database boyutu
        db_size = os.path.getsize(db_path) / (1024 * 1024)
        logging.info(f"Database boyutu: {db_size:.2f} MB")
        
        conn.close()
        
    except Exception as e:
        logging.error(f"\nHata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    optimize_database()

