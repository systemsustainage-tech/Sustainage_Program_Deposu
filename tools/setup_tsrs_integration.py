#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS-GRI-SDG Entegrasyon Kurulum Scripti
Gerçek verilerle eşleştirmeleri oluşturur
"""

import logging
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def setup_tsrs_gri_mappings() -> None:
    """TSRS-GRI eşleştirmelerini oluştur"""
    logging.info("TSRS-GRI eslestirmeleri olusturuluyor...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Mevcut GRI-TSRS eşleştirmelerinden TSRS-GRI eşleştirmeleri oluştur
        cursor.execute("""
            INSERT OR REPLACE INTO map_tsrs_gri 
            (tsrs_standard_code, tsrs_indicator_code, gri_standard, gri_disclosure, relationship_type, notes)
            SELECT 
                tsrs_section,
                tsrs_metric,
                gri_standard,
                gri_disclosure,
                relation_type,
                notes
            FROM map_gri_tsrs
        """)
        
        conn.commit()
        logging.info("TSRS-GRI eslestirmeleri basariyla olusturuldu")
        
        # Eşleştirme sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM map_tsrs_gri")
        count = cursor.fetchone()[0]
        logging.info(f"Toplam TSRS-GRI eslestirmesi: {count}")
        
        return True
        
    except Exception as e:
        logging.error(f"TSRS-GRI eslestirmeleri olusturulurken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def setup_tsrs_sdg_mappings() -> None:
    """TSRS-SDG eşleştirmelerini oluştur"""
    logging.info("TSRS-SDG eslestirmeleri olusturuluyor...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # TSRS standartları ile SDG hedefleri arasında mantıklı eşleştirmeler oluştur
        tsrs_sdg_mappings = [
            # Yönetişim - SDG 16 (Barış, Adalet ve Güçlü Kurumlar)
            ('TSRS-001', None, 16, None, None, 'direct', 'Yönetişim yapısı ve sorumluluklar'),
            
            # Strateji - SDG 12 (Sorumlu Tüketim ve Üretim)
            ('TSRS-002', None, 12, None, None, 'direct', 'Sürdürülebilirlik stratejisi ve hedefler'),
            
            # Risk Yönetimi - SDG 13 (İklim Eylemi)
            ('TSRS-003', None, 13, None, None, 'direct', 'İklim değişikliği ve çevresel riskler'),
            
            # Metrikler - Çevresel SDG'ler
            ('TSRS-004', None, 13, None, None, 'direct', 'Karbon emisyonları - İklim eylemi'),
            ('TSRS-005', None, 7, None, None, 'direct', 'Enerji kullanımı - Erişilebilir ve temiz enerji'),
            ('TSRS-006', None, 6, None, None, 'direct', 'Su kullanımı - Temiz su ve sanitasyon'),
            ('TSRS-007', None, 12, None, None, 'direct', 'Atık yönetimi - Sorumlu tüketim'),
            
            # Sosyal Metrikler - Sosyal SDG'ler
            ('TSRS-008', None, 8, None, None, 'direct', 'Çalışan hakları - İnsana yakışır iş'),
            ('TSRS-009', None, 10, None, None, 'direct', 'Toplumsal etki - Eşitsizliklerin azaltılması'),
            ('TSRS-010', None, 12, None, None, 'direct', 'Tedarik zinciri - Sorumlu tüketim'),
        ]
        
        for mapping in tsrs_sdg_mappings:
            cursor.execute("""
                INSERT OR REPLACE INTO map_tsrs_sdg 
                (tsrs_standard_code, tsrs_indicator_code, sdg_goal_id, sdg_target_id, 
                 sdg_indicator_code, relationship_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, mapping)
        
        conn.commit()
        logging.info("TSRS-SDG eslestirmeleri basariyla olusturuldu")
        
        # Eşleştirme sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM map_tsrs_sdg")
        count = cursor.fetchone()[0]
        logging.info(f"Toplam TSRS-SDG eslestirmesi: {count}")
        
        return True
        
    except Exception as e:
        logging.error(f"TSRS-SDG eslestirmeleri olusturulurken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_comprehensive_mappings() -> None:
    """Kapsamlı eşleştirmeler oluştur"""
    logging.info("Kapsamli eslestirmeler olusturuluyor...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # TSRS standartlarına gösterge ekle
        tsrs_indicators = [
            # TSRS-001: Yönetişim
            (1, 'TSRS-001-1', 'Yönetim Kurulu Sürdürülebilirlik Sorumluluğu', 
             'Yönetim kurulunun sürdürülebilirlik konularındaki sorumlulukları', 'Metin', 'Yönetim kurulu üyelerinin sürdürülebilirlik eğitimleri'),
            (1, 'TSRS-001-2', 'Sürdürülebilirlik Komitesi', 
             'Sürdürülebilirlik komitesinin oluşumu ve faaliyetleri', 'Evet/Hayır', 'Komite üye sayısı ve toplantı sıklığı'),
            
            # TSRS-002: Strateji
            (2, 'TSRS-002-1', 'Sürdürülebilirlik Vizyonu ve Misyonu', 
             'Şirketin sürdürülebilirlik vizyonu ve misyonu', 'Metin', 'Vizyon ve misyonun paydaşlarla paylaşımı'),
            (2, 'TSRS-002-2', 'Sürdürülebilirlik Hedefleri', 
             'Belirlenen sürdürülebilirlik hedefleri', 'Metin', 'Hedeflerin ölçülebilirliği ve zaman çerçevesi'),
            
            # TSRS-003: Risk Yönetimi
            (3, 'TSRS-003-1', 'İklim Risk Değerlendirmesi', 
             'İklim değişikliği risklerinin değerlendirilmesi', 'Metin', 'Risk değerlendirme metodolojisi'),
            (3, 'TSRS-003-2', 'Çevresel Risk Matrisi', 
             'Çevresel risklerin matris formatında değerlendirilmesi', 'Metin', 'Risk seviyesi ve önlemler'),
            
            # TSRS-004: Karbon Emisyonları
            (4, 'TSRS-004-1', 'Kapsam 1 Emisyonları', 
             'Doğrudan sera gazı emisyonları', 'Ton CO2e', 'ISO 14064-1 standardına uygun hesaplama'),
            (4, 'TSRS-004-2', 'Kapsam 2 Emisyonları', 
             'Enerji tüketiminden kaynaklanan dolaylı emisyonlar', 'Ton CO2e', 'Elektrik ve ısıtma tüketimi'),
            (4, 'TSRS-004-3', 'Kapsam 3 Emisyonları', 
             'Değer zincirindeki diğer dolaylı emisyonlar', 'Ton CO2e', 'Tedarik zinciri ve ulaşım emisyonları'),
            
            # TSRS-005: Enerji
            (5, 'TSRS-005-1', 'Toplam Enerji Tüketimi', 
             'Toplam enerji tüketimi', 'MWh', 'Elektrik, doğalgaz, fuel-oil tüketimi'),
            (5, 'TSRS-005-2', 'Yenilenebilir Enerji Oranı', 
             'Yenilenebilir enerji kullanım oranı', '%', 'Güneş, rüzgar, hidroelektrik enerji'),
            
            # TSRS-006: Su
            (6, 'TSRS-006-1', 'Toplam Su Tüketimi', 
             'Toplam su tüketimi', 'm³', 'Şebeke suyu ve kuyu suyu tüketimi'),
            (6, 'TSRS-006-2', 'Su Verimliliği', 
             'Su verimlilik göstergeleri', 'm³/ton ürün', 'Birim ürün başına su tüketimi'),
            
            # TSRS-007: Atık
            (7, 'TSRS-007-1', 'Toplam Atık Üretimi', 
             'Toplam atık üretimi', 'Ton', 'Tehlikeli ve tehlikesiz atık'),
            (7, 'TSRS-007-2', 'Geri Dönüşüm Oranı', 
             'Geri dönüşüm oranı', '%', 'Geri dönüştürülen atık oranı'),
            
            # TSRS-008: Çalışan Hakları
            (8, 'TSRS-008-1', 'Çalışan Sayısı', 
             'Toplam çalışan sayısı', 'Kişi', 'Tam zamanlı ve yarı zamanlı çalışanlar'),
            (8, 'TSRS-008-2', 'İş Kazası Sayısı', 
             'İş kazası sayısı', 'Adet', 'Kayıp zamanlı iş kazaları'),
            
            # TSRS-009: Toplumsal Etki
            (9, 'TSRS-009-1', 'Sosyal Sorumluluk Projeleri', 
             'Sosyal sorumluluk projelerinin sayısı', 'Adet', 'Tamamlanan projeler'),
            (9, 'TSRS-009-2', 'Toplumsal Yatırım Tutarı', 
             'Toplumsal yatırım tutarı', 'TL', 'Sosyal sorumluluk projelerine ayrılan bütçe'),
            
            # TSRS-010: Tedarik Zinciri
            (10, 'TSRS-010-1', 'Tedarikçi Sayısı', 
             'Toplam tedarikçi sayısı', 'Adet', 'Aktif tedarikçi sayısı'),
            (10, 'TSRS-010-2', 'Tedarikçi Sürdürülebilirlik Değerlendirmesi', 
             'Sürdürülebilirlik değerlendirmesi yapılan tedarikçi oranı', '%', 'Sürdürülebilirlik kriterlerine göre değerlendirilen tedarikçiler')
        ]
        
        for indicator in tsrs_indicators:
            cursor.execute("""
                INSERT OR REPLACE INTO tsrs_indicators 
                (standard_id, code, title, description, data_type, methodology, is_mandatory, is_quantitative)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                indicator[0], indicator[1], indicator[2], indicator[3], 
                indicator[4], indicator[5], 1 if indicator[4] in ['Ton CO2e', 'MWh', 'm³', 'Ton', 'Kişi', 'Adet', 'TL', '%'] else 0
            ))
        
        conn.commit()
        logging.info("TSRS gostergeleri basariyla olusturuldu")
        
        # Gösterge sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
        count = cursor.fetchone()[0]
        logging.info(f"Toplam TSRS gostergesi: {count}")
        
        return True
        
    except Exception as e:
        logging.error(f"TSRS gostergeleri olusturulurken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_integration() -> None:
    """Entegrasyonu test et"""
    logging.info("TSRS-GRI-SDG entegrasyonu test ediliyor...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # TSRS-GRI eşleştirmelerini test et
        cursor.execute("""
            SELECT COUNT(*) FROM map_tsrs_gri tg
            JOIN tsrs_standards ts ON tg.tsrs_standard_code = ts.code
            JOIN gri_standards gs ON tg.gri_standard = gs.code
        """)
        tsrs_gri_count = cursor.fetchone()[0]
        logging.info(f"Gecerli TSRS-GRI eslestirmesi: {tsrs_gri_count}")
        
        # TSRS-SDG eşleştirmelerini test et
        cursor.execute("""
            SELECT COUNT(*) FROM map_tsrs_sdg tsd
            JOIN tsrs_standards ts ON tsd.tsrs_standard_code = ts.code
            JOIN sdg_goals sg ON tsd.sdg_goal_id = sg.id
        """)
        tsrs_sdg_count = cursor.fetchone()[0]
        logging.info(f"Gecerli TSRS-SDG eslestirmesi: {tsrs_sdg_count}")
        
        # TSRS göstergelerini test et
        cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
        indicators_count = cursor.fetchone()[0]
        logging.info(f"Toplam TSRS gostergesi: {indicators_count}")
        
        return True
        
    except Exception as e:
        logging.error(f"Entegrasyon test edilirken hata: {e}")
        return False
    finally:
        conn.close()

def main() -> None:
    """Ana kurulum fonksiyonu"""
    logging.info("TSRS-GRI-SDG Entegrasyon Kurulum Baslatiliyor...")
    logging.info("=" * 60)
    
    success_count = 0
    total_tasks = 4
    
    # 1. TSRS-GRI eşleştirmelerini oluştur
    if setup_tsrs_gri_mappings():
        success_count += 1
    
    # 2. TSRS-SDG eşleştirmelerini oluştur
    if setup_tsrs_sdg_mappings():
        success_count += 1
    
    # 3. TSRS göstergelerini oluştur
    if create_comprehensive_mappings():
        success_count += 1
    
    # 4. Entegrasyonu test et
    if test_integration():
        success_count += 1
    
    logging.info("=" * 60)
    logging.info(f"TSRS-GRI-SDG Entegrasyon Kurulum Tamamlandi: {success_count}/{total_tasks} basarili")
    
    if success_count == total_tasks:
        logging.info("Tum TSRS-GRI-SDG entegrasyon ozellikleri basariyla kuruldu!")
        logging.info("\nEntegrasyon Ozellikleri:")
        logging.info("  - TSRS-GRI Eslestirmeleri")
        logging.info("  - TSRS-SDG Eslestirmeleri")
        logging.info("  - TSRS GOSTergeleri")
        logging.info("  - Kapsamli Eslestirme Testleri")
        logging.info("\nTSRS-GRI-SDG entegrasyonu kullanima hazir!")
        return True
    else:
        logging.error("Bazi ozellikler kurulamadi. Lutfen hatalari kontrol edin.")
        return False

if __name__ == "__main__":
    main()
