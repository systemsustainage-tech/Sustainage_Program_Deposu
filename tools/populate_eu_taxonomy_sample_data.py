#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
EU Taxonomy için Örnek Veri Ekleme Aracı
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
        logging.error(f'Silent error in populate_eu_taxonomy_sample_data.py: {str(e)}')

def populate_eu_taxonomy_sample_data() -> None:
    """EU Taxonomy için örnek veriler ekle"""
    
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
        
        # EU Taxonomy örnek faaliyetleri
        logging.info(f"{Icons.EU_FLAG} EU Taxonomy örnek faaliyetleri ekleniyor...")
        
        sample_activities = [
            {
                'code': 'ACT-001',
                'name': 'Yenilenebilir Enerji Üretimi',
                'sector': 'Enerji',
                'revenue_alignment': 25.5,
                'capex_alignment': 40.0,
                'opex_alignment': 15.0,
                'status': 'Uyumlu',
                'environmental_objectives': ['İklim Değişikliği Azaltma', 'İklim Değişikliği Adaptasyonu']
            },
            {
                'code': 'ACT-002',
                'name': 'Enerji Verimliliği İyileştirmeleri',
                'sector': 'Enerji',
                'revenue_alignment': 12.3,
                'capex_alignment': 18.7,
                'opex_alignment': 8.9,
                'status': 'Uyumlu',
                'environmental_objectives': ['İklim Değişikliği Azaltma']
            },
            {
                'code': 'ACT-003',
                'name': 'Elektrikli Araç Filosu',
                'sector': 'Ulaştırma',
                'revenue_alignment': 8.1,
                'capex_alignment': 22.4,
                'opex_alignment': 5.6,
                'status': 'Uygun',
                'environmental_objectives': ['İklim Değişikliği Azaltma', 'Kirliliğin Önlenmesi ve Kontrolü']
            },
            {
                'code': 'ACT-004',
                'name': 'Su Geri Kazanım Sistemi',
                'sector': 'Su ve Atık Yönetimi',
                'revenue_alignment': 5.2,
                'capex_alignment': 12.8,
                'opex_alignment': 3.4,
                'status': 'Uyumlu',
                'environmental_objectives': ['Su ve Deniz Kaynaklarının Sürdürülebilir Kullanımı']
            },
            {
                'code': 'ACT-005',
                'name': 'Döngüsel Ekonomi Projeleri',
                'sector': 'Çevre Koruma',
                'revenue_alignment': 15.8,
                'capex_alignment': 25.3,
                'opex_alignment': 12.1,
                'status': 'Uyumlu',
                'environmental_objectives': ['Döngüsel Ekonomiye Geçiş', 'Biyoçeşitlilik ve Ekosistemlerin Korunması']
            },
            {
                'code': 'ACT-006',
                'name': 'Yeşil Bina Sertifikasyonu',
                'sector': 'İnşaat',
                'revenue_alignment': 18.6,
                'capex_alignment': 35.2,
                'opex_alignment': 9.8,
                'status': 'Uyumlu',
                'environmental_objectives': ['İklim Değişikliği Azaltma', 'İklim Değişikliği Adaptasyonu']
            },
            {
                'code': 'ACT-007',
                'name': 'Sürdürülebilir Tarım Uygulamaları',
                'sector': 'Tarım',
                'revenue_alignment': 22.4,
                'capex_alignment': 28.9,
                'opex_alignment': 16.7,
                'status': 'Uygun',
                'environmental_objectives': ['Biyoçeşitlilik ve Ekosistemlerin Korunması', 'Kirliliğin Önlenmesi ve Kontrolü']
            },
            {
                'code': 'ACT-008',
                'name': 'Orman Koruma ve Restorasyon',
                'sector': 'Orman',
                'revenue_alignment': 7.9,
                'capex_alignment': 15.6,
                'opex_alignment': 4.2,
                'status': 'Uyumlu',
                'environmental_objectives': ['İklim Değişikliği Azaltma', 'Biyoçeşitlilik ve Ekosistemlerin Korunması']
            },
            {
                'code': 'ACT-009',
                'name': 'Dijital Teknoloji Çözümleri',
                'sector': 'Bilgi ve İletişim',
                'revenue_alignment': 35.2,
                'capex_alignment': 45.8,
                'opex_alignment': 28.4,
                'status': 'Değerlendirme Bekliyor',
                'environmental_objectives': ['İklim Değişikliği Azaltma']
            },
            {
                'code': 'ACT-010',
                'name': 'Karbon Yakalama ve Depolama',
                'sector': 'Enerji',
                'revenue_alignment': 3.7,
                'capex_alignment': 8.3,
                'opex_alignment': 2.1,
                'status': 'Uygun Değil',
                'environmental_objectives': ['İklim Değişikliği Azaltma']
            }
        ]
        
        # Önce eu_taxonomy_activities tablosuna faaliyetleri ekle
        for activity in sample_activities:
            # EU Taxonomy activities tablosuna ekle
            cursor.execute("""
                INSERT OR REPLACE INTO eu_taxonomy_activities 
                (activity_code, activity_name, activity_name_tr, sector, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                activity['code'],
                activity['name'],
                activity['name'],
                activity['sector'],
                f"Örnek faaliyet: {activity['name']}",
                datetime.now().isoformat()
            ))
            
            # Activity ID'yi al
            cursor.execute("SELECT id FROM eu_taxonomy_activities WHERE activity_code = ?", (activity['code'],))
            activity_id = cursor.fetchone()[0]
            
            # Company taxonomy activities tablosuna ekle
            cursor.execute("""
                INSERT OR REPLACE INTO company_taxonomy_activities 
                (company_id, activity_id, period, revenue_share, capex_share, opex_share, 
                 is_eligible, is_aligned, alignment_status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                activity_id,
                '2024',
                activity['revenue_alignment'],
                activity['capex_alignment'],
                activity['opex_alignment'],
                activity['status'] in ['Uygun', 'Uyumlu'],
                activity['status'] == 'Uyumlu',
                activity['status'],
                f"Çevresel hedefler: {', '.join(activity['environmental_objectives'])}",
                datetime.now().isoformat()
            ))
        
        # Değişiklikleri kaydet
        conn.commit()
        logging.info(" EU Taxonomy örnek faaliyetleri başarıyla eklendi!")
        
        # Veri sayısını göster
        cursor.execute("SELECT COUNT(*) FROM company_taxonomy_activities WHERE company_id = ?", (company_id,))
        activity_count = cursor.fetchone()[0]
        
        logging.info(f" Toplam Faaliyet: {activity_count}")
        
        # KPI özeti
        cursor.execute("""
            SELECT 
                AVG(revenue_share) as avg_revenue,
                AVG(capex_share) as avg_capex,
                AVG(opex_share) as avg_opex,
                COUNT(CASE WHEN is_aligned = 1 THEN 1 END) as aligned_count,
                COUNT(CASE WHEN is_eligible = 1 THEN 1 END) as eligible_count
            FROM company_taxonomy_activities 
            WHERE company_id = ?
        """, (company_id,))
        
        stats = cursor.fetchone()
        if stats:
            logging.info(f" Ortalama Gelir Uyumu: {stats[0]:.1f}%")
            logging.info(f" Ortalama CapEx Uyumu: {stats[1]:.1f}%")
            logging.info(f" Ortalama OpEx Uyumu: {stats[2]:.1f}%")
            logging.info(f" Uyumlu Faaliyetler: {stats[3]}")
            logging.info(f" Uygun Faaliyetler: {stats[4]}")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    populate_eu_taxonomy_sample_data()
