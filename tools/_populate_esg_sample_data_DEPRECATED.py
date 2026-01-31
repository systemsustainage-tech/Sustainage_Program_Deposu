#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
ESG Modülü için Örnek Veri Ekleme Aracı
"""

import os
import sqlite3
import sys
from datetime import datetime
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Windows terminal için UTF-8 desteği
if os.name == 'nt' and not os.getenv('PYTEST_CURRENT_TEST'):
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError) as e:
        logging.error(f'Silent error in populate_esg_sample_data.py: {str(e)}')

def populate_esg_sample_data() -> None:
    """ESG modülü için örnek veriler ekle"""
    
    # Veritabanı yolu
    db_path = DB_PATH
    
    if not os.path.exists(db_path):
        logging.info(" Veritabanı bulunamadı:", db_path)
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Şirket ID'sini kontrol et
        cursor.execute("SELECT id FROM companies LIMIT 1")
        company_result = cursor.fetchone()
        
        if not company_result:
            # Varsayılan şirket ekle
            cursor.execute("""
                INSERT INTO companies (name, sector, country, created_at)
                VALUES (?, ?, ?, ?)
            """, ('Örnek Şirket', 'Teknoloji', 'Türkiye', datetime.now().isoformat()))
            company_id = cursor.lastrowid
        else:
            company_id = company_result[0]
        
        logging.info(f" Şirket ID: {company_id}")
        
        # GRI örnek verileri ekle
        logging.info(" GRI örnek verileri ekleniyor...")
        
        # Environmental (E) verileri
        environmental_data = [
            ('GRI 302-1', 'Enerji tüketimi', '2023', '150,000 kWh', 'Environmental'),
            ('GRI 302-2', 'Enerji tüketimi yoğunluğu', '2023', '0.8 kWh/m²', 'Environmental'),
            ('GRI 303-1', 'Su çekimi', '2023', '500,000 m³', 'Environmental'),
            ('GRI 303-3', 'Su tüketimi', '2023', '480,000 m³', 'Environmental'),
            ('GRI 305-1', 'Direkt GHG emisyonları', '2023', '2,500 tCO2e', 'Environmental'),
            ('GRI 305-2', 'Enerji dolaylı GHG emisyonları', '2023', '1,800 tCO2e', 'Environmental'),
            ('GRI 306-1', 'Atık üretimi', '2023', '45 ton', 'Environmental'),
            ('GRI 306-2', 'Tehlikeli atık', '2023', '12 ton', 'Environmental')
        ]
        
        # Social (S) verileri
        social_data = [
            ('GRI 401-1', 'Yeni işe alımlar', '2023', '25 kişi', 'Social'),
            ('GRI 401-2', 'İşten çıkarma oranı', '2023', '%3.2', 'Social'),
            ('GRI 403-1', 'İş sağlığı ve güvenliği politikası', '2023', 'Uygulanıyor', 'Social'),
            ('GRI 403-2', 'İş kazaları', '2023', '2 kaza', 'Social'),
            ('GRI 404-1', 'Eğitim saatleri', '2023', '1,200 saat', 'Social'),
            ('GRI 405-1', 'Çeşitlilik oranı', '2023', '%35 kadın', 'Social'),
            ('GRI 406-1', 'Ayrımcılık olayları', '2023', '0 olay', 'Social'),
            ('GRI 412-1', 'İnsan hakları politikası', '2023', 'Uygulanıyor', 'Social')
        ]
        
        # Governance (G) verileri
        governance_data = [
            ('GRI 2-1', 'Organizasyon yapısı', '2023', 'Kurumsal', 'GRI 2'),
            ('GRI 2-2', 'Yönetim kurulu kompozisyonu', '2023', '7 üye', 'GRI 2'),
            ('GRI 2-3', 'Bağımsız yönetim kurulu üyeleri', '2023', '4 üye', 'GRI 2'),
            ('GRI 2-4', 'Etik ve uyum politikası', '2023', 'Uygulanıyor', 'GRI 2'),
            ('GRI 2-5', 'Risk yönetimi', '2023', 'Aktif', 'GRI 2'),
            ('GRI 2-6', 'Paydaş katılımı', '2023', 'Düzenli', 'GRI 2')
        ]
        
        # Tüm verileri ekle
        all_data = environmental_data + social_data + governance_data
        
        for code, title, period, value, source in all_data:
            # Önce indicator_id'yi bul
            cursor.execute("""
                SELECT gi.id FROM gri_indicators gi
                JOIN gri_standards gs ON gi.standard_id = gs.id
                WHERE gi.code = ? AND gs.category = ?
            """, (code, source))
            
            indicator_result = cursor.fetchone()
            
            if indicator_result:
                indicator_id = indicator_result[0]
                
                # Response'u ekle
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_responses 
                    (company_id, indicator_id, response_value, period, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, indicator_id, value, period, datetime.now().isoformat()))
        
        # TSRS örnek verileri ekle
        logging.info(" TSRS örnek verileri ekleniyor...")
        
        tsrs_data = [
            ('TSRS-E1-1', 'Karbon ayak izi', 'TSRS-E1', 'Environmental', '2023', '2,500 tCO2e'),
            ('TSRS-E1-2', 'Enerji verimliliği', 'TSRS-E1', 'Environmental', '2023', '%15 artış'),
            ('TSRS-E2-1', 'Su yönetimi', 'TSRS-E2', 'Environmental', '2023', '500,000 m³'),
            ('TSRS-E3-1', 'Atık yönetimi', 'TSRS-E3', 'Environmental', '2023', '45 ton'),
            ('TSRS-S1-1', 'İş güvenliği', 'TSRS-S1', 'Social', '2023', '2 kaza'),
            ('TSRS-S1-2', 'Çalışan memnuniyeti', 'TSRS-S1', 'Social', '2023', '%85'),
            ('TSRS-S2-1', 'Toplumsal katkı', 'TSRS-S2', 'Social', '2023', '₺50,000'),
            ('TSRS-G1-1', 'Etik yönetim', 'TSRS-G1', 'Governance', '2023', 'Uygulanıyor'),
            ('TSRS-G1-2', 'Risk yönetimi', 'TSRS-G1', 'Governance', '2023', 'Aktif')
        ]
        
        for code, title, standard_code, category, period, value in tsrs_data:
            # Indicator ID'yi bul
            cursor.execute("""
                SELECT ti.id FROM tsrs_indicators ti
                JOIN tsrs_standards ts ON ti.standard_id = ts.id
                WHERE ti.code = ? AND ts.category = ?
            """, (code, category))
            
            indicator_result = cursor.fetchone()
            
            if indicator_result:
                indicator_id = indicator_result[0]
                
                # Response'u ekle
                cursor.execute("""
                    INSERT OR REPLACE INTO tsrs_responses 
                    (company_id, indicator_id, response_value, reporting_period, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, indicator_id, value, period, datetime.now().isoformat()))
        
        # Değişiklikleri kaydet
        conn.commit()
        logging.info(" ESG örnek verileri başarıyla eklendi!")
        
        # Veri sayılarını göster
        cursor.execute("SELECT COUNT(*) FROM gri_responses WHERE company_id = ?", (company_id,))
        gri_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tsrs_responses WHERE company_id = ?", (company_id,))
        tsrs_count = cursor.fetchone()[0]
        
        logging.info(f" GRI Responses: {gri_count}")
        logging.info(f" TSRS Responses: {tsrs_count}")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    populate_esg_sample_data()
