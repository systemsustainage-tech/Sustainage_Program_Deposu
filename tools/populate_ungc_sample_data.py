#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Örnek Veri Ekleme Scripti
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def populate_ungc_sample_data() -> None:
    """UNGC örnek verilerini ekle"""
    
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
        
        logging.info("UNGC ornek verileri ekleniyor...")
        
        # UNGC tablolarını oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ungc_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                principle_id VARCHAR(10) NOT NULL,
                compliance_level VARCHAR(20) DEFAULT 'None',
                evidence_count INTEGER DEFAULT 0,
                score REAL DEFAULT 0.0,
                last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ungc_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                principle_id VARCHAR(10) NOT NULL,
                evidence_type VARCHAR(50) NOT NULL,
                evidence_description TEXT,
                evidence_source VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # 1. UNGC Uyumluluk Durumları Ekle
        logging.info("UNGC uyumluluk durumlari ekleniyor...")
        
        compliance_data = [
            {
                'principle_id': 'P1',
                'compliance_level': 'Full',
                'evidence_count': 3,
                'score': 0.85,
                'notes': 'İnsan hakları politikası mevcut, eğitimler düzenleniyor'
            },
            {
                'principle_id': 'P2',
                'compliance_level': 'Full',
                'evidence_count': 2,
                'score': 0.90,
                'notes': 'Due diligence süreçleri uygulanıyor'
            },
            {
                'principle_id': 'P3',
                'compliance_level': 'Partial',
                'evidence_count': 2,
                'score': 0.65,
                'notes': 'Sendika diyaloğu mevcut, geliştirme alanları var'
            },
            {
                'principle_id': 'P4',
                'compliance_level': 'Full',
                'evidence_count': 3,
                'score': 0.95,
                'notes': 'Zorla çalıştırma politikası ve denetimleri mevcut'
            },
            {
                'principle_id': 'P5',
                'compliance_level': 'Full',
                'evidence_count': 3,
                'score': 0.95,
                'notes': 'Çocuk işçiliği politikası ve denetimleri mevcut'
            },
            {
                'principle_id': 'P6',
                'compliance_level': 'Partial',
                'evidence_count': 2,
                'score': 0.70,
                'notes': 'Eşitlik politikası mevcut, metrikler geliştiriliyor'
            },
            {
                'principle_id': 'P7',
                'compliance_level': 'Full',
                'evidence_count': 4,
                'score': 0.80,
                'notes': 'Çevre politikası ve hedefler mevcut'
            },
            {
                'principle_id': 'P8',
                'compliance_level': 'Partial',
                'evidence_count': 3,
                'score': 0.75,
                'notes': 'Çevre programları mevcut, metrikler artırılıyor'
            },
            {
                'principle_id': 'P9',
                'compliance_level': 'Partial',
                'evidence_count': 2,
                'score': 0.60,
                'notes': 'Yeşil teknoloji yatırımları başlatıldı'
            },
            {
                'principle_id': 'P10',
                'compliance_level': 'Full',
                'evidence_count': 4,
                'score': 0.88,
                'notes': 'Yolsuzlukla mücadele politikası ve eğitimler mevcut'
            }
        ]
        
        for compliance in compliance_data:
            cursor.execute("""
                INSERT OR REPLACE INTO ungc_compliance 
                (company_id, principle_id, compliance_level, evidence_count, score, notes, last_assessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                compliance['principle_id'],
                compliance['compliance_level'],
                compliance['evidence_count'],
                compliance['score'],
                compliance['notes'],
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(compliance_data)} UNGC uyumluluk durumu eklendi")
        
        # 2. UNGC Kanıt Verileri Ekle
        logging.info("UNGC kanit verileri ekleniyor...")
        
        evidence_data = [
            # P1 - İnsan Hakları
            {'principle_id': 'P1', 'evidence_type': 'policy', 'evidence_description': 'İnsan Hakları Politikası', 'evidence_source': 'İK Departmanı'},
            {'principle_id': 'P1', 'evidence_type': 'training', 'evidence_description': 'İnsan Hakları Eğitimi', 'evidence_source': 'Eğitim Departmanı'},
            {'principle_id': 'P1', 'evidence_type': 'grievance', 'evidence_description': 'Şikayet Mekanizması', 'evidence_source': 'Etik Komitesi'},
            
            # P2 - İnsan Hakları İhlali
            {'principle_id': 'P2', 'evidence_type': 'policy', 'evidence_description': 'Due Diligence Politikası', 'evidence_source': 'Risk Yönetimi'},
            {'principle_id': 'P2', 'evidence_type': 'due_diligence', 'evidence_description': 'Tedarikçi Değerlendirme Raporu', 'evidence_source': 'Satın Alma'},
            
            # P3 - Örgütlenme Özgürlüğü
            {'principle_id': 'P3', 'evidence_type': 'policy', 'evidence_description': 'Sendika Diyaloğu Politikası', 'evidence_source': 'İK Departmanı'},
            {'principle_id': 'P3', 'evidence_type': 'union_dialogue', 'evidence_description': 'Toplu İş Sözleşmesi', 'evidence_source': 'Sendika'},
            
            # P4 - Zorla Çalıştırma
            {'principle_id': 'P4', 'evidence_type': 'policy', 'evidence_description': 'Zorla Çalıştırma Politikası', 'evidence_source': 'İK Departmanı'},
            {'principle_id': 'P4', 'evidence_type': 'audits', 'evidence_description': 'Çalışma Koşulları Denetimi', 'evidence_source': 'Denetim Departmanı'},
            {'principle_id': 'P4', 'evidence_type': 'audits', 'evidence_description': 'Tedarikçi Denetim Raporu', 'evidence_source': 'Satın Alma'},
            
            # P5 - Çocuk İşçiliği
            {'principle_id': 'P5', 'evidence_type': 'policy', 'evidence_description': 'Çocuk İşçiliği Politikası', 'evidence_source': 'İK Departmanı'},
            {'principle_id': 'P5', 'evidence_type': 'audits', 'evidence_description': 'Yaş Doğrulama Denetimi', 'evidence_source': 'Denetim Departmanı'},
            {'principle_id': 'P5', 'evidence_type': 'audits', 'evidence_description': 'Tedarikçi Yaş Denetimi', 'evidence_source': 'Satın Alma'},
            
            # P6 - Ayrımcılık
            {'principle_id': 'P6', 'evidence_type': 'policy', 'evidence_description': 'Eşitlik ve Çeşitlilik Politikası', 'evidence_source': 'İK Departmanı'},
            {'principle_id': 'P6', 'evidence_type': 'metrics', 'evidence_description': 'İşe Alım Çeşitlilik Raporu', 'evidence_source': 'İK Departmanı'},
            
            # P7 - Çevre Önlem Yaklaşımı
            {'principle_id': 'P7', 'evidence_type': 'policy', 'evidence_description': 'Çevre Politikası', 'evidence_source': 'Çevre Departmanı'},
            {'principle_id': 'P7', 'evidence_type': 'targets', 'evidence_description': 'Karbon Azaltma Hedefleri', 'evidence_source': 'Sürdürülebilirlik'},
            {'principle_id': 'P7', 'evidence_type': 'targets', 'evidence_description': 'Su Tasarrufu Hedefleri', 'evidence_source': 'Çevre Departmanı'},
            {'principle_id': 'P7', 'evidence_type': 'targets', 'evidence_description': 'Atık Azaltma Hedefleri', 'evidence_source': 'Çevre Departmanı'},
            
            # P8 - Çevresel Sorumluluk
            {'principle_id': 'P8', 'evidence_type': 'programs', 'evidence_description': 'Çevre Yönetim Sistemi', 'evidence_source': 'Çevre Departmanı'},
            {'principle_id': 'P8', 'evidence_type': 'metrics', 'evidence_description': 'Çevre Performans Raporu', 'evidence_source': 'Sürdürülebilirlik'},
            {'principle_id': 'P8', 'evidence_type': 'programs', 'evidence_description': 'ISO 14001 Sertifikası', 'evidence_source': 'Kalite'},
            
            # P9 - Yeşil Teknoloji
            {'principle_id': 'P9', 'evidence_type': 'innovation', 'evidence_description': 'Yeşil Teknoloji Ar-Ge Projesi', 'evidence_source': 'Ar-Ge'},
            {'principle_id': 'P9', 'evidence_type': 'investments', 'evidence_description': 'Temiz Enerji Yatırımı', 'evidence_source': 'Finans'},
            
            # P10 - Yolsuzlukla Mücadele
            {'principle_id': 'P10', 'evidence_type': 'policy', 'evidence_description': 'Yolsuzlukla Mücadele Politikası', 'evidence_source': 'Etik Komitesi'},
            {'principle_id': 'P10', 'evidence_type': 'training', 'evidence_description': 'Etik Eğitimi', 'evidence_source': 'Eğitim Departmanı'},
            {'principle_id': 'P10', 'evidence_type': 'incidents', 'evidence_description': 'Etik İhlal Raporu', 'evidence_source': 'Etik Komitesi'},
            {'principle_id': 'P10', 'evidence_type': 'training', 'evidence_description': 'Yolsuzlukla Mücadele Eğitimi', 'evidence_source': 'Eğitim Departmanı'}
        ]
        
        for evidence in evidence_data:
            cursor.execute("""
                INSERT OR REPLACE INTO ungc_evidence 
                (company_id, principle_id, evidence_type, evidence_description, evidence_source, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                evidence['principle_id'],
                evidence['evidence_type'],
                evidence['evidence_description'],
                evidence['evidence_source'],
                datetime.now().isoformat()
            ))
        
        logging.info(f"OK {len(evidence_data)} UNGC kanit verisi eklendi")
        
        # Degisiklikleri kaydet
        conn.commit()
        
        logging.info("\nUNGC ornek verileri basariyla eklendi!")
        logging.info("\nOzet:")
        logging.info(f"- Uyumluluk Durumlari: {len(compliance_data)}")
        logging.info(f"- Kanit Verileri: {len(evidence_data)}")
        
        return True
        
    except Exception as e:
        logging.error(f"UNGC ornek veri ekleme hatasi: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = populate_ungc_sample_data()
    if success:
        logging.info("\nUNGC ornek verileri basariyla eklendi!")
    else:
        logging.error("\nUNGC ornek verileri eklenirken hata olustu!")
        sys.exit(1)
