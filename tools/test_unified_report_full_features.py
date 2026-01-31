
import os
import sys
import logging
import sqlite3
from datetime import datetime

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from backend.modules.reporting.unified_report_docx import UnifiedReportDocxGenerator

logging.basicConfig(level=logging.INFO)

def populate_test_data(db_path, company_id, period):
    """Ensure necessary test data exists for all sections."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. CEO Messages
        cur.execute("CREATE TABLE IF NOT EXISTS ceo_messages (id INTEGER PRIMARY KEY, company_id INTEGER, period TEXT, message_type TEXT, title TEXT, content TEXT, year INTEGER, quarter INTEGER, signature_name TEXT, signature_title TEXT, signature_date TEXT, key_achievements TEXT, challenges TEXT, future_commitments TEXT)")
        cur.execute("DELETE FROM ceo_messages WHERE company_id=? AND period=?", (company_id, period))
        cur.execute("""
            INSERT INTO ceo_messages (company_id, period, message_type, title, content, year, signature_name, signature_title)
            VALUES (?, ?, 'annual', 'Sürdürülebilirlik Yolculuğumuz', 'Bu yıl harika işler başardık. Hedeflerimize ulaştık.', ?, 'Ahmet Yılmaz', 'CEO')
        """, (company_id, period, int(period)))
        
        # 2. SDG Validation Results (Mock)
        cur.execute("CREATE TABLE IF NOT EXISTS sdg_validation_results (id INTEGER PRIMARY KEY, company_id INTEGER, rule_id INTEGER, validation_status TEXT, validation_date TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS sdg_validation_rules (id INTEGER PRIMARY KEY, rule_name TEXT)")
        # Insert a rule if not exists
        cur.execute("INSERT OR IGNORE INTO sdg_validation_rules (id, rule_name) VALUES (1, 'Eksik Veri Kontrolü')")
        
        # 3. SDG Data Quality Scores
        cur.execute("CREATE TABLE IF NOT EXISTS sdg_data_quality_scores (id INTEGER PRIMARY KEY, company_id INTEGER, validation_date TEXT, completeness_score REAL, accuracy_score REAL, consistency_score REAL, timeliness_score REAL, overall_quality_score REAL)")
        cur.execute("DELETE FROM sdg_data_quality_scores WHERE company_id=?", (company_id,))
        cur.execute("""
            INSERT INTO sdg_data_quality_scores (company_id, validation_date, completeness_score, accuracy_score, consistency_score, timeliness_score, overall_quality_score)
            VALUES (?, ?, 95.0, 98.0, 90.0, 100.0, 95.75)
        """, (company_id, datetime.now().isoformat()))

        # 4. UNGC (Mock tables if needed, usually managed by UNGCManager)
        # We assume UNGCManager handles its own tables or they exist.
        
        # 5. GRI Selections (Mock)
        cur.execute("CREATE TABLE IF NOT EXISTS gri_selections (id INTEGER PRIMARY KEY, company_id INTEGER, indicator_id INTEGER, selected INTEGER)")
        # Need actual indicator IDs, but let's assume some exist or skip if empty.

        # 6. UNGC Compliance
        cur.execute("""
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
        cur.execute("DELETE FROM ungc_compliance WHERE company_id=?", (company_id,))
        
        # UNGC Principles (1-10)
        ungc_principles = [
            ('P1', 'Full', 100.0, 2),
            ('P2', 'Full', 90.0, 1),
            ('P3', 'Partial', 60.0, 1),
            ('P4', 'Full', 95.0, 3),
            ('P5', 'Full', 100.0, 2),
            ('P6', 'Full', 100.0, 1),
            ('P7', 'Partial', 50.0, 0),
            ('P8', 'Full', 85.0, 2),
            ('P9', 'Full', 100.0, 3),
            ('P10', 'Full', 95.0, 1)
        ]
        
        for pid, level, score, ev_count in ungc_principles:
            cur.execute("""
                INSERT INTO ungc_compliance (company_id, principle_id, compliance_level, score, evidence_count, notes)
                VALUES (?, ?, ?, ?, ?, 'Test compliance note')
            """, (company_id, pid, level, score, ev_count))

        # 7. UNGC Evidence
        cur.execute("""
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
        cur.execute("DELETE FROM ungc_evidence WHERE company_id=?", (company_id,))
        
        # Sample evidence
        cur.execute("""
            INSERT INTO ungc_evidence (company_id, principle_id, evidence_type, evidence_description, evidence_source)
            VALUES (?, 'P1', 'Policy', 'Human Rights Policy Document', 'HR Department')
        """, (company_id,))
        
        # 8. Materiality Topics (Mock)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS materiality_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                sdg_mapping TEXT,
                priority_score REAL DEFAULT 0,
                stakeholder_impact REAL DEFAULT 0,
                business_impact REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("DELETE FROM materiality_topics WHERE company_id=?", (company_id,))
        cur.execute("""
            INSERT INTO materiality_topics (company_id, topic_name, category, stakeholder_impact, business_impact, priority_score)
            VALUES 
            (?, 'İklim Değişikliği', 'Çevresel', 4.5, 4.8, 9.3),
            (?, 'Çalışan Hakları', 'Sosyal', 4.2, 3.9, 8.1),
            (?, 'Veri Güvenliği', 'Yönetişim', 3.8, 4.5, 8.3)
        """, (company_id, company_id, company_id))

        # 9. ESRS Disclosures (Mock)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS esrs_disclosures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                esrs_standard TEXT NOT NULL,
                disclosure_code TEXT NOT NULL,
                disclosure_name TEXT NOT NULL,
                is_required BOOLEAN DEFAULT 0,
                is_material BOOLEAN DEFAULT 0,
                completion_status TEXT DEFAULT 'tamamlanmadi',
                disclosure_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("DELETE FROM esrs_disclosures WHERE company_id=?", (company_id,))
        cur.execute("""
            INSERT INTO esrs_disclosures (company_id, esrs_standard, disclosure_code, disclosure_name, is_material, completion_status)
            VALUES 
            (?, 'E1', 'E1-1', 'Transition plan for climate change', 1, 'tamamlandi'),
            (?, 'E1', 'E1-2', 'Policies related to climate change', 1, 'tamamlandi'),
            (?, 'E1', 'E1-3', 'Actions and resources', 1, 'devam_ediyor'),
            (?, 'S1', 'S1-1', 'Policies related to own workforce', 1, 'tamamlandi')
        """, (company_id, company_id, company_id, company_id))

        # 10. Company Targets (Mock)
        cur.execute("DROP TABLE IF EXISTS company_targets")
        cur.execute("""
            CREATE TABLE company_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                category TEXT,
                metric_type TEXT,
                baseline_year INTEGER,
                target_year INTEGER,
                baseline_value REAL,
                target_value REAL,
                current_value REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("DELETE FROM company_targets WHERE company_id=?", (company_id,))
        cur.execute("""
            INSERT INTO company_targets (company_id, category, metric_type, baseline_year, target_year, baseline_value, target_value, status)
            VALUES 
            (?, 'environment', 'carbon_reduction', 2020, 2030, 1000.0, 500.0, 'on_track'),
            (?, 'social', 'gender_diversity', 2022, 2025, 30.0, 50.0, 'achieved')
        """, (company_id, company_id))

        # 11. Supplier Environmental Data (Mock)
        cur.execute("DROP TABLE IF EXISTS supplier_environmental_data")
        cur.execute("""
            CREATE TABLE supplier_environmental_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                period TEXT,
                energy_consumption REAL,
                emissions REAL,
                waste_amount REAL,
                water_consumption REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # We don't link by company_id here per the code in unified_report_docx (it just queries by period for now)
        cur.execute("DELETE FROM supplier_environmental_data WHERE period=?", (period,))
        cur.execute("""
            INSERT INTO supplier_environmental_data (supplier_id, period, energy_consumption, emissions, waste_amount, water_consumption)
            VALUES 
            (101, ?, 5000.0, 120.5, 50.0, 1000.0),
            (102, ?, 7500.0, 200.0, 80.0, 1500.0)
        """, (period, period))

        conn.commit()
        logging.info("Test data populated successfully (CEO, SDG, Quality, UNGC, Materiality, ESRS, Targets, Supply Chain).")
    except Exception as e:
        logging.error(f"Error populating test data: {e}")
    finally:
        conn.close()

def test_full_report_generation():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    generator = UnifiedReportDocxGenerator(base_dir)
    
    # Use existing DB path from generator
    db_path = generator.db_path
    company_id = 1
    period = "2024"
    
    # Populate test data
    populate_test_data(db_path, company_id, period)
    
    # Mock generation parameters
    report_name = "Full Feature Test Report"
    selected_modules = ["SDG", "GRI", "UNGC", "ESG"]
    module_reports = [
        {"module_code": "SDG", "report_name": "SDG Raporu", "report_type": "PDF", "reporting_period": "2024", "created_at": "2024-12-01"},
        {"module_code": "GRI", "report_name": "GRI İndeksi", "report_type": "DOCX", "reporting_period": "2024", "created_at": "2024-12-05"}
    ]
    ai_comment = "Yapay zeka analizi: Şirket performansı artış trendinde.\nÖzellikle su yönetimi konusunda iyileşmeler var."
    description = "Bu rapor, 2024 yılı sürdürülebilirlik performansını kapsar."
    metrics = {
        'carbon': {'total_co2e': 1250.5, 'scope_breakdown': [{'scope': 'Scope 1', 'co2e': 500}, {'scope': 'Scope 2', 'co2e': 750}]},
        'water': {'total_consumption': 3000, 'source_breakdown': [{'water_source': 'Şebeke', 'consumption': 3000}]},
        'taxonomy': {
            'total_revenue': 1000000, 'aligned_revenue': 250000, 'alignment_percentage_revenue': 25.0,
            'total_capex': 500000, 'aligned_capex': 100000, 'alignment_percentage_capex': 20.0,
            'total_opex': 200000, 'aligned_opex': 10000, 'alignment_percentage_opex': 5.0
        },
        'stakeholder_survey': {
            'survey_title': '2024 Paydaş Katılım Anketi',
            'survey_description': 'Şirketimizin önceliklerini belirlemek için yapılan yıllık anket.',
            'response_count': 150,
            'created_at': '2024-11-15',
            'insights_text': 'Paydaşlar özellikle iklim değişikliği ve çalışan haklarına odaklanmıştır.',
            'top3': [
                {'question': 'İklim Değişikliği Eylemi', 'avg_score': 4.8},
                {'question': 'Çalışan Refahı', 'avg_score': 4.6},
                {'question': 'Etik İş Uygulamaları', 'avg_score': 4.5}
            ],
            'bottom3': [
                {'question': 'Yerel Topluluk Katılımı', 'avg_score': 3.2},
                {'question': 'Su Yönetimi', 'avg_score': 3.5}
            ],
            'questions': [
                {'goal': 13, 'question': 'İklim Değişikliği Eylemi', 'avg_score': 4.8, 'response_count': 150},
                {'goal': 8, 'question': 'Çalışan Refahı', 'avg_score': 4.6, 'response_count': 148},
                {'goal': 16, 'question': 'Etik İş Uygulamaları', 'avg_score': 4.5, 'response_count': 145},
                {'goal': 6, 'question': 'Su Yönetimi', 'avg_score': 3.5, 'response_count': 140},
                {'goal': 11, 'question': 'Yerel Topluluk Katılımı', 'avg_score': 3.2, 'response_count': 135}
            ]
        }
    }
    
    logging.info(f"Generating report for Company {company_id}, Period {period}...")
    
    output_path = generator.generate(
        company_id, period, report_name, selected_modules, 
        module_reports, ai_comment, description, metrics
    )
    
    if output_path and os.path.exists(output_path):
        logging.info(f"SUCCESS: Report generated at {output_path}")
        logging.info(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        logging.error("FAILURE: Report generation failed or file not found.")

if __name__ == "__main__":
    test_full_report_generation()
