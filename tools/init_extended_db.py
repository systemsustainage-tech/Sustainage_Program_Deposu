#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genişletilmiş SDG Veritabanı Başlatma
- Temel şema + yeni modüller
- Önceliklendirme tabloları
- Ürün/Teknoloji tabloları
"""

import logging
import argparse
import os
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_sql(conn, path) -> None:
    """SQL dosyasını çalıştır"""
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)

def create_extended_tables(conn) -> None:
    """Genişletilmiş tabloları oluştur"""
    cursor = conn.cursor()
    
    # Önceliklendirme tabloları
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS survey_templates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'Genel',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
        """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiality_topics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            sdg_mapping TEXT,
            priority_score REAL DEFAULT 0,
            stakeholder_impact REAL DEFAULT 0,
            business_impact REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholder_surveys (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            survey_name TEXT NOT NULL,
            stakeholder_category TEXT NOT NULL,
            survey_data TEXT, -- JSON format
            total_responses INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS survey_questions (
            id INTEGER PRIMARY KEY,
            template_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL, -- multiple_choice, scale, text, boolean
            weight REAL DEFAULT 1.0,
            category TEXT,
            sdg_mapping TEXT,
            FOREIGN KEY(template_id) REFERENCES survey_templates(id) ON DELETE CASCADE
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            response_value TEXT,
            score REAL DEFAULT 0,
            response_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prioritization_results (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            total_score REAL NOT NULL,
            priority_level TEXT NOT NULL, -- high, medium, low
            calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
        """
    )
    
    # İnovasyon tabloları
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS innovation_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            rd_investment_ratio REAL, -- Toplam ciro içindeki AR-GE oranı (%)
            rd_investment_amount REAL, -- AR-GE yatırım miktarı (TL)
            patent_applications INTEGER DEFAULT 0, -- Patent başvuru sayısı
            utility_models INTEGER DEFAULT 0, -- Faydalı model sayısı
            patents_granted INTEGER DEFAULT 0, -- Verilen patent sayısı
            ecodesign_integration BOOLEAN DEFAULT 0, -- Eko-tasarım entegrasyonu
            lca_implementation BOOLEAN DEFAULT 0, -- LCA uygulaması
            innovation_budget REAL, -- İnovasyon bütçesi (TL)
            innovation_projects INTEGER DEFAULT 0, -- Aktif inovasyon proje sayısı
            sustainability_innovation_ratio REAL, -- Sürdürülebilir inovasyon oranı (%)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS innovation_projects (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            project_type TEXT, -- R&D, P&D, Sustainability, Digital
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            status TEXT DEFAULT 'active', -- active, completed, cancelled
            sdg_mapping TEXT, -- İlgili SDG hedefleri
            sustainability_focus BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intellectual_property (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            ip_type TEXT NOT NULL, -- patent, utility_model, trademark, copyright
            title TEXT NOT NULL,
            application_number TEXT,
            application_date TEXT,
            grant_date TEXT,
            status TEXT, -- applied, granted, rejected, expired
            description TEXT,
            sdg_mapping TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    # Kalite tabloları
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quality_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            iso9001_certified BOOLEAN DEFAULT 0, -- ISO 9001 sertifikası
            iso14001_certified BOOLEAN DEFAULT 0, -- ISO 14001 sertifikası
            iso45001_certified BOOLEAN DEFAULT 0, -- ISO 45001 sertifikası
            customer_complaint_rate REAL, -- Müşteri şikayet oranı (%)
            customer_complaint_count INTEGER DEFAULT 0, -- Şikayet sayısı
            product_recall_count INTEGER DEFAULT 0, -- Ürün geri çağırma sayısı
            nps_score REAL, -- Net Promoter Score
            customer_satisfaction_score REAL, -- Müşteri memnuniyet skoru (1-10)
            quality_error_rate REAL, -- Kalite kontrol hata oranı (%)
            defect_rate REAL, -- Defekt oranı (%)
            first_pass_yield REAL, -- İlk geçiş verimliliği (%)
            supplier_quality_score REAL, -- Tedarikçi kalite skoru (1-10)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quality_certifications (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            certification_type TEXT NOT NULL, -- ISO 9001, ISO 14001, vb.
            certification_body TEXT, -- Sertifika veren kuruluş
            certificate_number TEXT,
            issue_date TEXT,
            expiry_date TEXT,
            status TEXT DEFAULT 'active', -- active, expired, suspended
            scope TEXT, -- Sertifika kapsamı
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_surveys (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            survey_name TEXT NOT NULL,
            survey_type TEXT, -- NPS, CSAT, CES
            survey_date TEXT,
            total_responses INTEGER DEFAULT 0,
            average_score REAL,
            promoter_percentage REAL, -- NPS için
            detractor_percentage REAL, -- NPS için
            passive_percentage REAL, -- NPS için
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    # Dijital güvenlik tabloları
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS digital_security_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            iso27001_certified BOOLEAN DEFAULT 0, -- ISO 27001 sertifikası
            cybersecurity_training_hours REAL, -- Siber güvenlik eğitim saatleri
            data_breach_count INTEGER DEFAULT 0, -- Veri ihlali sayısı
            data_breach_severity TEXT, -- Düşük, Orta, Yüksek, Kritik
            digital_transformation_budget REAL, -- Dijital dönüşüm bütçesi
            ai_applications_count INTEGER DEFAULT 0, -- AI uygulama sayısı
            cloud_adoption_percentage REAL, -- Bulut kullanım oranı (%)
            automation_percentage REAL, -- Otomasyon oranı (%)
            digital_literacy_score REAL, -- Dijital okuryazarlık skoru (1-10)
            cybersecurity_incidents INTEGER DEFAULT 0, -- Siber güvenlik olayları
            incident_response_time REAL, -- Olay müdahale süresi (saat)
            backup_frequency TEXT, -- Yedekleme sıklığı
            disaster_recovery_plan BOOLEAN DEFAULT 0, -- Afet kurtarma planı
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    # Acil durum yönetimi tabloları
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            business_continuity_plan BOOLEAN DEFAULT 0, -- İş sürekliliği planı
            emergency_response_team BOOLEAN DEFAULT 0, -- Acil durum ekibi
            risk_assessment_matrix BOOLEAN DEFAULT 0, -- Risk değerlendirme matrisi
            emergency_drills_count INTEGER DEFAULT 0, -- Acil durum tatbikat sayısı
            drill_participation_rate REAL, -- Tatbikat katılım oranı (%)
            insurance_coverage REAL, -- Sigorta kapsamı (TL)
            emergency_contacts_count INTEGER DEFAULT 0, -- Acil durum iletişim sayısı
            evacuation_plan BOOLEAN DEFAULT 0, -- Tahliye planı
            communication_plan BOOLEAN DEFAULT 0, -- İletişim planı
            backup_systems_count INTEGER DEFAULT 0, -- Yedek sistem sayısı
            recovery_time_objective REAL, -- Kurtarma süre hedefi (saat)
            maximum_tolerable_downtime REAL, -- Maksimum kabul edilebilir kesinti (saat)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            risk_category TEXT NOT NULL, -- Doğal, Teknolojik, İnsan, Finansal
            risk_description TEXT NOT NULL,
            probability_score INTEGER, -- Olasılık skoru (1-5)
            impact_score INTEGER, -- Etki skoru (1-5)
            risk_level TEXT, -- Düşük, Orta, Yüksek, Kritik
            mitigation_measures TEXT, -- Azaltma önlemleri
            responsible_person TEXT, -- Sorumlu kişi
            review_date TEXT, -- İnceleme tarihi
            status TEXT DEFAULT 'active', -- active, mitigated, closed
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()

def insert_sample_data(conn) -> None:
    """Örnek veri ekle"""
    cursor = conn.cursor()
    
    # Örnek şirket
    cursor.execute("""
        INSERT OR IGNORE INTO companies (id, name, sector, country)
        VALUES (1, 'Örnek Şirket A.Ş.', 'Teknoloji', 'Türkiye')
    """)
    
    # Örnek kullanıcılar
    #  GÜVENLİK: Argon2 kullanılıyor (SHA-256 kaldırıldı)
    from yonetim.security.core.crypto import hash_password

    # Normal admin kullanıcısı
    admin_password_hash = hash_password("admin123")
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, display_name, email, password_hash, role, is_active)
        VALUES (1, 'admin', 'Sistem Yöneticisi', 'admin@sustainage.tr', ?, 'super_admin', 1)
    """, (admin_password_hash,))
    
    # Özel super admin kullanıcısı
    super_password_hash = hash_password("Kayra_1507")
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, display_name, email, password_hash, role, is_active)
        VALUES (999, '__super__', 'Kayra Super Admin', 'kayra@sustainage.tr', ?, 'super_admin', 1)
    """, (super_password_hash,))
    
    # Örnek materyal konular
    materiality_topics = [
        (1, 'İklim Değişikliği', 'Çevresel', 'Karbon emisyonları ve iklim etkisi', 'SDG 13'),
        (1, 'Dijital Dönüşüm', 'Teknolojik', 'Dijitalleşme ve inovasyon', 'SDG 9'),
        (1, 'Çalışan Memnuniyeti', 'Sosyal', 'İnsan kaynakları ve çalışan hakları', 'SDG 8'),
        (1, 'Etik Yönetim', 'Yönetişim', 'Etik iş uygulamaları ve şeffaflık', 'SDG 16'),
    ]
    
    for company_id, topic_name, category, description, sdg_mapping in materiality_topics:
        cursor.execute("""
            INSERT OR IGNORE INTO materiality_topics 
            (company_id, topic_name, category, description, sdg_mapping)
            VALUES (?, ?, ?, ?, ?)
        """, (company_id, topic_name, category, description, sdg_mapping))
    
    conn.commit()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Veritabanı dosya yolu")
    ap.add_argument("--schema", default="schema.sql", help="Temel şema dosyası")
    ap.add_argument("--seed", default="data/seeds/seed_sdg.sql", help="SDG seed dosyası")
    ap.add_argument("--plus", default="data/seeds/seed_plus.sql", help="Plus seed dosyası")
    args = ap.parse_args()

    # Dosya varlığını kontrol et
    if not os.path.exists(args.schema):
        sys.exit(f"Şema dosyası bulunamadı: {args.schema}")
    if not os.path.exists(args.seed):
        sys.exit(f"Seed dosyası bulunamadı: {args.seed}")
    if not os.path.exists(args.plus):
        sys.exit(f"Plus seed dosyası bulunamadı: {args.plus}")

    # Veritabanını oluştur
    conn = sqlite3.connect(args.db)
    
    try:
        # Temel şemayı yükle
        run_sql(conn, args.schema)
        run_sql(conn, args.seed)
        run_sql(conn, args.plus)
        
        # Genişletilmiş tabloları oluştur
        create_extended_tables(conn)
        
        # Örnek veri ekleme (varsayılan kapalı - üretim güvenliği)
        allow_samples = os.getenv("ALLOW_SAMPLE_DATA", "False") == "True"
        if allow_samples:
            insert_sample_data(conn)
        else:
            logging.info("[SKIP] Örnek veri ekleme devre dışı (ALLOW_SAMPLE_DATA=False)")
        
        logging.info(f"Genisletilmis veritabani basariyla olusturuldu: {args.db}")
        logging.info("Eklenen moduller:")
        logging.info("   - Onceliklendirme Analizi")
        logging.info("   - Inovasyon & AR-GE")
        logging.info("   - Kalite Yonetimi")
        logging.info("   - Dijital Guvenlik")
        logging.info("   - Acil Durum Yonetimi")
        
    except Exception as e:
        logging.error(f"Hata olustu: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
