#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 Örnek Veri Ekleme Scripti
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def populate_scope3_sample_data() -> None:
    """Scope 3 örnek verilerini ekle"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabani bulunamadi: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Örnek şirket ID'si (varsayılan: 1)
        company_id = 1
        
        logging.info("Scope 3 ornek verileri ekleniyor...")
        
        # Scope 3 tablolarını oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope3_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_number INTEGER UNIQUE NOT NULL,
                category_name TEXT NOT NULL,
                description TEXT,
                scope_type TEXT DEFAULT 'Indirect',
                is_upstream BOOLEAN DEFAULT 1,
                is_downstream BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope3_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                activity_data REAL,
                activity_unit TEXT,
                emission_factor REAL,
                emission_factor_unit TEXT,
                total_emissions REAL,
                reporting_period TEXT,
                data_source TEXT,
                methodology TEXT,
                uncertainty_level TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id),
                FOREIGN KEY(category_id) REFERENCES scope3_categories(id)
            )
        """)
        
        # 1. Scope 3 Kategorileri Ekle
        logging.info("Scope 3 kategorileri ekleniyor...")
        
        categories_data = [
            (1, '1. Satın Alınan Mal ve Hizmetler', 'Tedarikçilerden satın alınan mal ve hizmetlerin üretiminden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (2, '2. Sermaye Malları', 'Sermaye mallarının üretiminden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (3, '3. Yakıt ve Enerji Faaliyetleri', 'Yakıt ve enerji faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (4, '4. Nakliye ve Dağıtım', 'Nakliye ve dağıtım faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (5, '5. Üretilen Ürünlerin Kullanımı', 'Üretilen ürünlerin kullanımından kaynaklanan emisyonlar', 'Indirect', 0, 1),
            (6, '6. İş Seyahatleri', 'Çalışanların iş seyahatlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (7, '7. Çalışanların İşe Gidiş-Gelişleri', 'Çalışanların işe gidiş-gelişlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (8, '8. Kiralanan Varlıklar', 'Kiralanan varlıklardan kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (9, '9. Yatırımlar', 'Yatırım faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (10, '10. Tedarik Zinciri Dışı Nakliye', 'Tedarik zinciri dışı nakliye faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 1, 0),
            (11, '11. İşlenmiş Ürünlerin Kullanımı', 'İşlenmiş ürünlerin kullanımından kaynaklanan emisyonlar', 'Indirect', 0, 1),
            (12, '12. Tedarik Zinciri Dışı Dağıtım', 'Tedarik zinciri dışı dağıtım faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 0, 1),
            (13, '13. Satılan Ürünlerin Bertarafı', 'Satılan ürünlerin bertarafından kaynaklanan emisyonlar', 'Indirect', 0, 1),
            (14, '14. Kiralanan Varlıkların Kullanımı', 'Kiralanan varlıkların kullanımından kaynaklanan emisyonlar', 'Indirect', 0, 1),
            (15, '15. Franchising', 'Franchising faaliyetlerinden kaynaklanan emisyonlar', 'Indirect', 0, 1)
        ]
        
        for category in categories_data:
            cursor.execute("""
                INSERT OR IGNORE INTO scope3_categories 
                (category_number, category_name, description, scope_type, is_upstream, is_downstream)
                VALUES (?, ?, ?, ?, ?, ?)
            """, category)
        
        logging.info(f"OK {len(categories_data)} Scope 3 kategorisi eklendi")
        
        # 2. Scope 3 Emisyon Verileri Ekle
        logging.info("Scope 3 emisyon verileri ekleniyor...")
        
        # Kategori ID'lerini al
        cursor.execute("SELECT id, category_number FROM scope3_categories")
        category_mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        emissions_data = [
            {
                'category_id': category_mapping[1],
                'activity_data': 1500000.0,
                'activity_unit': 'TL',
                'emission_factor': 0.0005,
                'total_emissions': 750.0,
                'reporting_period': '2024',
                'data_source': 'Muhasebe Sistemi',
                'notes': 'Satın alınan mal ve hizmetler için genel emisyon faktörü kullanıldı'
            },
            {
                'category_id': category_mapping[2],
                'activity_data': 500000.0,
                'activity_unit': 'TL',
                'emission_factor': 0.0012,
                'total_emissions': 600.0,
                'reporting_period': '2024',
                'data_source': 'Mali Raporlar',
                'notes': 'Makine ve ekipman yatırımları'
            },
            {
                'category_id': category_mapping[3],
                'activity_data': 2000000.0,
                'activity_unit': 'kWh',
                'emission_factor': 0.0003,
                'total_emissions': 600.0,
                'reporting_period': '2024',
                'data_source': 'Enerji Sistemi',
                'notes': 'Elektrik tüketimi ve yakıt kullanımı'
            },
            {
                'category_id': category_mapping[4],
                'activity_data': 25000.0,
                'activity_unit': 'km',
                'emission_factor': 0.02,
                'total_emissions': 500.0,
                'reporting_period': '2024',
                'data_source': 'Lojistik Sistemi',
                'notes': 'Kargo ve nakliye hizmetleri'
            },
            {
                'category_id': category_mapping[5],
                'activity_data': 100000.0,
                'activity_unit': 'adet',
                'emission_factor': 0.015,
                'total_emissions': 1500.0,
                'reporting_period': '2024',
                'data_source': 'Satış Raporları',
                'notes': 'Üretilen ürünlerin kullanım süresi boyunca emisyonları'
            },
            {
                'category_id': category_mapping[6],
                'activity_data': 5000.0,
                'activity_unit': 'km',
                'emission_factor': 0.12,
                'total_emissions': 600.0,
                'reporting_period': '2024',
                'data_source': 'İnsan Kaynakları',
                'notes': 'Uçak, tren ve araç ile iş seyahatleri'
            },
            {
                'category_id': category_mapping[7],
                'activity_data': 150000.0,
                'activity_unit': 'km',
                'emission_factor': 0.08,
                'total_emissions': 12000.0,
                'reporting_period': '2024',
                'data_source': 'İnsan Kaynakları',
                'notes': 'Çalışanların ev-iş arası ulaşımı'
            },
            {
                'category_id': category_mapping[8],
                'activity_data': 300000.0,
                'activity_unit': 'TL',
                'emission_factor': 0.0008,
                'total_emissions': 240.0,
                'reporting_period': '2024',
                'data_source': 'Muhasebe Sistemi',
                'notes': 'Ofis ve depo kiralama giderleri'
            },
            {
                'category_id': category_mapping[9],
                'activity_data': 1000000.0,
                'activity_unit': 'TL',
                'emission_factor': 0.0003,
                'total_emissions': 300.0,
                'reporting_period': '2024',
                'data_source': 'Mali Raporlar',
                'notes': 'Yatırım portföyü emisyonları'
            },
            {
                'category_id': category_mapping[10],
                'activity_data': 8000.0,
                'activity_unit': 'km',
                'emission_factor': 0.025,
                'total_emissions': 200.0,
                'reporting_period': '2024',
                'data_source': 'Lojistik Sistemi',
                'notes': 'Müşterilere teslimat nakliyesi'
            }
        ]
        
        for emission in emissions_data:
            cursor.execute("""
                INSERT OR IGNORE INTO scope3_emissions 
                (company_id, category_id, activity_data, activity_unit, emission_factor, 
                 total_emissions, reporting_period, data_source, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                emission['category_id'],
                emission['activity_data'],
                emission['activity_unit'],
                emission['emission_factor'],
                emission['total_emissions'],
                emission['reporting_period'],
                emission['data_source'],
                emission['notes'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(emissions_data)} Scope 3 emisyon verisi eklendi")
        
        # Degisiklikleri kaydet
        conn.commit()
        
        logging.info("\nScope 3 ornek verileri basariyla eklendi!")
        logging.info("\nOzet:")
        logging.info(f"- Kategoriler: {len(categories_data)}")
        logging.info(f"- Emisyon Verileri: {len(emissions_data)}")
        logging.info(f"- Toplam Emisyon: {sum(e['total_emissions'] for e in emissions_data):.1f} tCO2e")
        
        return True
        
    except Exception as e:
        logging.error(f"Scope 3 ornek veri ekleme hatasi: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = populate_scope3_sample_data()
    if success:
        logging.info("\nScope 3 ornek verileri basariyla eklendi!")
    else:
        logging.error("\nScope 3 ornek verileri eklenirken hata olustu!")
        sys.exit(1)
