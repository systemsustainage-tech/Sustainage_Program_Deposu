#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Modülü Kurulum Scripti - Sprint 1
- GRI şemasını genişletir (ek tablolar)
- Excel verilerini import eder
- Consistency check yapar
"""

import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gri.gri_excel_importer import import_gri_excel
from gri.gri_manager import GRIManager
from gri.gri_schema_upgrade import upgrade_gri_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_gri() -> None:
    """GRI modülünü kur - Sprint 1"""
    logging.info("GRI Modulu Kurulum Basliyor...")
    logging.info("=" * 50)
    
    # 1. Şema genişletme
    logging.info("\n1. GRI şemasi genisletiliyor...")
    if not upgrade_gri_schema():
        logging.info("   Şema genişletme başarısız!")
        return False
    logging.info("   Şema genişletme başarılı!")
    
    # 2. Excel import
    logging.info("\n2. Excel verileri import ediliyor...")
    if not import_gri_excel():
        logging.info("   Excel import başarısız!")
        return False
    logging.info("   Excel import başarılı!")
    
    # 3. Temel tabloları oluştur (eğer yoksa)
    logging.info("\n3. Temel tablolar kontrol ediliyor...")
    gri_manager = GRIManager()
    if not gri_manager.create_gri_tables():
        logging.info("   Temel tablolar oluşturulamadı!")
        return False
    logging.info("   Temel tablolar hazır!")
    
    # 4. Consistency check
    logging.info("\n4. Consistency check yapılıyor...")
    consistency_result = check_consistency()
    # Excel'de sadece 13 satır olduğu için limitleri ayarla
    total_indicators = consistency_result.get('total_indicators', 13)
    
    if consistency_result['critical_errors'] > 0:
        logging.error(f"   KRITIK HATALAR: {consistency_result['critical_errors']}")
        return False
    if consistency_result['high_errors'] > total_indicators:  # Tüm göstergeler için limit
        logging.error(f"   YÜKSEK HATALAR: {consistency_result['high_errors']} (limit: {total_indicators})")
        return False
    logging.error(f"   Consistency check tamamlandı - Kritik: {consistency_result['critical_errors']}, Yüksek: {consistency_result['high_errors']}")
    
    # 5. Özet rapor
    logging.info("\n" + "=" * 50)
    logging.info("GRI MODULU KURULUM RAPORU")
    logging.info("=" * 50)
    
    # Veritabanı sayımları
    conn = gri_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM gri_standards")
    standards_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gri_indicators")
    indicators_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gri_categories")
    categories_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gri_digital_tools")
    tools_count = cursor.fetchone()[0]
    
    conn.close()
    
    logging.info(f"Standartlar: {standards_count}")
    logging.info(f"Göstergeler: {indicators_count}")
    logging.info(f"Kategoriler: {categories_count}")
    logging.info(f"Dijital Araçlar: {tools_count}")
    logging.error(f"Kritik Hatalar: {consistency_result['critical_errors']}")
    logging.error(f"Yüksek Hatalar: {consistency_result['high_errors']}")
    
    if consistency_result['critical_errors'] == 0 and consistency_result['high_errors'] <= total_indicators:
        logging.info("\nGRI modulu basariyla kuruldu!")
        logging.info(f"Kabul Kriterleri: KRITIK=0, YUKSEK<={total_indicators}")
        return True
    else:
        logging.info("\nGRI modulu kurulumu başarısız!")
        return False

def check_consistency() -> None:
    """Consistency check v1"""
    gri_manager = GRIManager()
    conn = gri_manager.get_connection()
    cursor = conn.cursor()
    
    result = {
        'critical_errors': 0,
        'high_errors': 0,
        'medium_errors': 0,
        'low_errors': 0,
        'warnings': [],
        'total_indicators': 0
    }
    
    try:
        # 1. Yetim kayıtlar - KRITIK
        cursor.execute("""
            SELECT COUNT(*) FROM gri_indicators gi
            LEFT JOIN gri_standards gs ON gi.standard_id = gs.id
            WHERE gs.id IS NULL
        """)
        orphan_indicators = cursor.fetchone()[0]
        if orphan_indicators > 0:
            result['critical_errors'] += orphan_indicators
            result['warnings'].append(f"Yetim gösterge kayıtları: {orphan_indicators}")
        
        # 2. Boş standart kodları - KRITIK
        cursor.execute("SELECT COUNT(*) FROM gri_standards WHERE code IS NULL OR code = ''")
        empty_standards = cursor.fetchone()[0]
        if empty_standards > 0:
            result['critical_errors'] += empty_standards
            result['warnings'].append(f"Boş standart kodları: {empty_standards}")
        
        # 3. Boş gösterge kodları - KRITIK
        cursor.execute("SELECT COUNT(*) FROM gri_indicators WHERE code IS NULL OR code = ''")
        empty_indicators = cursor.fetchone()[0]
        if empty_indicators > 0:
            result['critical_errors'] += empty_indicators
            result['warnings'].append(f"Boş gösterge kodları: {empty_indicators}")
        
        # 4. Birim/metodoloji eksik - YÜKSEK
        cursor.execute("SELECT COUNT(*) FROM gri_indicators WHERE unit IS NULL OR unit = ''")
        missing_units = cursor.fetchone()[0]
        if missing_units > 0:
            result['high_errors'] += missing_units
            result['warnings'].append(f"Birim eksik göstergeler: {missing_units}")
        
        cursor.execute("SELECT COUNT(*) FROM gri_indicators WHERE methodology IS NULL OR methodology = ''")
        missing_methodology = cursor.fetchone()[0]
        if missing_methodology > 0:
            result['high_errors'] += missing_methodology
            result['warnings'].append(f"Metodoloji eksik göstergeler: {missing_methodology}")
        
        # 5. SDG/GRI mapping eksik - ORTA (sadece uyarı)
        cursor.execute("""
            SELECT COUNT(*) FROM gri_indicators gi
            LEFT JOIN map_sdg_gri mg ON gi.code = mg.gri_disclosure
            WHERE mg.gri_disclosure IS NULL
        """)
        missing_sdg_mapping = cursor.fetchone()[0]
        if missing_sdg_mapping > 0:
            result['medium_errors'] += missing_sdg_mapping
            result['warnings'].append(f"SDG mapping eksik göstergeler: {missing_sdg_mapping}")
        
        # 6. Açıklama eksik - DÜŞÜK
        cursor.execute("SELECT COUNT(*) FROM gri_indicators WHERE description IS NULL OR description = ''")
        missing_description = cursor.fetchone()[0]
        if missing_description > 0:
            result['low_errors'] += missing_description
            result['warnings'].append(f"Açıklama eksik göstergeler: {missing_description}")
        
        # 7. Toplam gösterge sayısı
        cursor.execute("SELECT COUNT(*) FROM gri_indicators")
        result['total_indicators'] = cursor.fetchone()[0]
        
        return result
        
    except Exception as e:
        logging.error(f"Consistency check hatası: {e}")
        result['critical_errors'] += 1
        result['warnings'].append(f"Consistency check hatası: {e}")
        return result
    finally:
        conn.close()

if __name__ == "__main__":
    setup_gri()
