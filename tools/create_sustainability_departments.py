#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sürdürülebilirlik ve SDG departmanlarını oluştur
"""

import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_sustainability_departments() -> None:
    """Sürdürülebilirlik ve SDG departmanlarını oluştur"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logging.info("Sürdürülebilirlik ve SDG departmanları oluşturuluyor...")
        
        # Sürdürülebilirlik departmanları
        sustainability_departments = [
            # Ana Sürdürülebilirlik Departmanları
            ('Sürdürülebilirlik Yönetimi', 'SY', 'Sürdürülebilirlik stratejisi ve yönetimi'),
            ('ESG Yönetimi', 'ESG', 'ESG (Environmental, Social, Governance) yönetimi'),
            ('SDG Koordinasyonu', 'SDG', 'Sürdürülebilir Kalkınma Amaçları koordinasyonu'),
            ('Sürdürülebilir Raporlama', 'SR', 'Sürdürülebilirlik raporlama ve iletişim'),
            
            # Çevre Departmanları
            ('Çevre Yönetimi', 'CY', 'Çevresel etki yönetimi ve sürdürülebilirlik'),
            ('İklim Değişikliği', 'ID', 'İklim değişikliği stratejisi ve adaptasyon'),
            ('Enerji Yönetimi', 'EY', 'Sürdürülebilir enerji yönetimi'),
            ('Atık Yönetimi', 'AY', 'Atık azaltma ve döngüsel ekonomi'),
            ('Su Yönetimi', 'SY', 'Su kaynakları yönetimi'),
            
            # Sosyal Departmanlar
            ('İnsan Hakları', 'IH', 'İnsan hakları ve sosyal etki yönetimi'),
            ('Çalışan Sağlığı ve Güvenliği', 'CSG', 'İş sağlığı ve güvenliği'),
            ('Toplumsal Yatırım', 'TY', 'Sosyal sorumluluk ve toplumsal yatırım'),
            ('Eşitlik ve Çeşitlilik', 'EC', 'Eşitlik, çeşitlilik ve kapsayıcılık'),
            ('Eğitim ve Gelişim', 'EG', 'Sürdürülebilirlik eğitimi ve kapasite geliştirme'),
            
            # Yönetişim Departmanları
            ('Etik ve Uyum', 'EU', 'Etik yönetimi ve uyum'),
            ('Risk Yönetimi', 'RY', 'Sürdürülebilirlik risk yönetimi'),
            ('Tedarik Zinciri Yönetimi', 'TZY', 'Sürdürülebilir tedarik zinciri'),
            ('Stakeholder İlişkileri', 'SI', 'Paydaş ilişkileri yönetimi'),
            
            # Teknik Departmanlar
            ('Veri Analizi ve Metrikler', 'VAM', 'Sürdürülebilirlik veri analizi'),
            ('İnovasyon ve Teknoloji', 'IT', 'Sürdürülebilir inovasyon ve teknoloji'),
            ('Ürün Sürdürülebilirliği', 'US', 'Ürün yaşam döngüsü yönetimi'),
            ('Sertifikasyon ve Standartlar', 'SS', 'Sürdürülebilirlik sertifikaları ve standartları'),
            
            # Finansal Departmanlar
            ('Sürdürülebilir Finansman', 'SF', 'Yeşil finansman ve ESG yatırımları'),
            ('Maliyet-Benefit Analizi', 'MBA', 'Sürdürülebilirlik projelerinin finansal analizi'),
            
            # İletişim ve Pazarlama
            ('Sürdürülebilir Pazarlama', 'SP', 'Sürdürülebilir marka ve pazarlama'),
            ('Kurumsal İletişim', 'KI', 'Sürdürülebilirlik iletişimi'),
            ('Dijital Sürdürülebilirlik', 'DS', 'Dijital dönüşüm ve sürdürülebilirlik'),
            
            # Özel Sektör Departmanları
            ('Sürdürülebilir Operasyonlar', 'SO', 'Operasyonel sürdürülebilirlik'),
            ('Müşteri Sürdürülebilirliği', 'MS', 'Müşteri deneyimi ve sürdürülebilirlik'),
            ('Partner İlişkileri', 'PI', 'Sürdürülebilir iş ortaklıkları'),
            
            # Kamu ve STK Departmanları
            ('Politika Geliştirme', 'PG', 'Sürdürülebilirlik politikaları'),
            ('Proje Yönetimi', 'PY', 'Sürdürülebilirlik projeleri yönetimi'),
            ('Kapasite Geliştirme', 'KG', 'Sürdürülebilirlik kapasite geliştirme'),
            ('Araştırma ve Geliştirme', 'ARG', 'Sürdürülebilirlik araştırmaları'),
            
            # GRI ve TSRS Departmanları
            ('GRI Raporlama', 'GRI', 'Global Reporting Initiative raporlama'),
            ('TSRS Koordinasyonu', 'TSRS', 'Türkiye Sürdürülebilirlik Raporlama Standartları'),
            ('KPI Yönetimi', 'KPI', 'Sürdürülebilirlik göstergeleri yönetimi'),
            ('Benchmarking', 'BEN', 'Sürdürülebilirlik kıyaslama ve analiz'),
            
            # Akademik ve Eğitim
            ('Sürdürülebilirlik Eğitimi', 'SE', 'Kurumsal sürdürülebilirlik eğitimi'),
            ('Araştırma Koordinasyonu', 'AK', 'Sürdürülebilirlik araştırma koordinasyonu'),
            ('Bilgi Yönetimi', 'BY', 'Sürdürülebilirlik bilgi ve dokümantasyon'),
            
            # Uluslararası İlişkiler
            ('Uluslararası İşbirliği', 'UI', 'Uluslararası sürdürülebilirlik işbirlikleri'),
            ('Standart Uyumluluğu', 'SU', 'Uluslararası standart uyumluluğu'),
            ('Global Ağlar', 'GA', 'Global sürdürülebilirlik ağları'),
        ]
        
        # Departmanları veritabanına ekle
        for dept_name, dept_code, dept_desc in sustainability_departments:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO departments (name, code, description)
                    VALUES (?, ?, ?)
                """, (dept_name, dept_code, dept_desc))
                logging.info(f"[OK] {dept_name} ({dept_code}) departmanı eklendi")
            except Exception as e:
                logging.error(f"[ERROR] {dept_name} departmanı eklenirken hata: {e}")
        
        # Mevcut departmanları da güncelle (varsa)
        existing_departments = [
            ('Genel Müdürlük', 'GM', 'Genel müdürlük departmanı'),
            ('İnsan Kaynakları', 'IK', 'İnsan kaynakları departmanı'),
            ('Bilgi İşlem', 'BIT', 'Bilgi işlem departmanı'),
            ('Finans', 'FN', 'Finans departmanı'),
            ('Kalite', 'KL', 'Kalite yönetimi departmanı'),
            ('Pazarlama', 'PZ', 'Pazarlama departmanı'),
            ('Satış', 'ST', 'Satış departmanı'),
            ('Üretim', 'UR', 'Üretim departmanı'),
            ('Satın Alma', 'SA', 'Satın alma departmanı'),
            ('Muhasebe', 'MU', 'Muhasebe departmanı'),
            ('Hukuk', 'HU', 'Hukuk departmanı'),
            ('İdari İşler', 'II', 'İdari işler departmanı'),
        ]
        
        for dept_name, dept_code, dept_desc in existing_departments:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO departments (name, code, description)
                    VALUES (?, ?, ?)
                """, (dept_name, dept_code, dept_desc))
                logging.info(f"[OK] {dept_name} ({dept_code}) departmanı eklendi")
            except Exception as e:
                logging.error(f"[ERROR] {dept_name} departmanı eklenirken hata: {e}")
        
        conn.commit()
        logging.info("[SUCCESS] Tüm departmanlar başarıyla oluşturuldu!")
        return True
        
    except Exception as e:
        logging.error(f"[ERROR] Departmanlar oluşturulurken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    create_sustainability_departments()
