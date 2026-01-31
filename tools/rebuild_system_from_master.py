import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Sistemi Master Verilerden Yeniden Oluşturma
C:\SDG\SDG_232.xlsx MASTER_232 sayfasından tüm sistemi yeniden oluşturur
"""

import os
import sqlite3
from datetime import datetime

import pandas as pd
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SystemRebuilder:
    """Sistemi master verilerden yeniden oluşturucu"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
        
        # self.excel_file = os.path.join(os.getcwd(), 'SDG_232.xlsx')
        # Relative path kullan
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.excel_file = os.path.join(base_dir, "SDG_232.xlsx")
    
    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def rebuild_system(self) -> None:
        """Tüm sistemi yeniden oluştur"""
        try:
            logging.info("Sistem master verilerden yeniden olusturuluyor...")
            
            # Excel dosyasını oku
            df = pd.read_excel(self.excel_file, sheet_name='MASTER_232')
            logging.info(f"Toplam {len(df)} gosterge yuklendi")
            
            # Mevcut veritabanını temizle
            self.clean_database()
            
            # Veritabanına kaydet
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # SDG hedeflerini yükle
            self.load_sdg_goals(cursor, df)
            
            # Alt hedefleri yükle
            self.load_sdg_targets(cursor, df)
            
            # Göstergeleri yükle
            self.load_sdg_indicators(cursor, df)
            
            # Soruları yükle
            self.load_sdg_questions(cursor, df)
            
            # GRI eşleştirmelerini yükle
            self.load_gri_mappings(cursor, df)
            
            # TSRS eşleştirmelerini yükle
            self.load_tsrs_mappings(cursor, df)
            
            # KPI/Metrikleri yükle
            self.load_kpi_metrics(cursor, df)
            
            # CSV dosyalarını oluştur
            self.create_csv_files(df)
            
            conn.commit()
            conn.close()
            
            logging.info("Tum sistem basariyla yeniden olusturuldu!")
            return True
            
        except Exception as e:
            logging.error(f"Sistem olusturulurken hata: {e}")
            return False
    
    def clean_database(self) -> None:
        """Mevcut veritabanını temizle"""
        logging.info("Mevcut veritabanı temizleniyor...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tüm tabloları sil
        tables_to_drop = [
            'sdg_question_responses', 'sdg_validation_results', 'sdg_data_quality_scores',
            'sdg_performance_metrics', 'sdg_kpi_metrics', 'map_gri_tsrs', 'map_sdg_tsrs',
            'map_sdg_gri', 'sdg_question_bank', 'sdg_question_types', 'sdg_indicators',
            'sdg_targets', 'sdg_goals'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        
        conn.commit()
        conn.close()
        
        # Yeni tabloları oluştur
        self.create_tables()
    
    def create_tables(self) -> None:
        """Tüm tabloları oluştur"""
        logging.info("Tablolar olusturuluyor...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SDG hedefleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code INTEGER UNIQUE NOT NULL,
                title_tr TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG alt hedefleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                title_tr TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES sdg_goals(id)
            )
        """)
        
        # SDG göstergeleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                title_tr TEXT NOT NULL,
                data_source TEXT,
                measurement_frequency TEXT,
                related_sectors TEXT,
                related_funds TEXT,
                kpi_metric TEXT,
                implementation_requirement TEXT,
                notes TEXT,
                request_status TEXT,
                status TEXT,
                progress_percentage REAL,
                completeness_percentage REAL,
                policy_document_exists TEXT,
                data_quality TEXT,
                incentive_readiness_score REAL,
                readiness_level TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES sdg_targets(id)
            )
        """)
        
        # SDG soru tipleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                description TEXT,
                input_type TEXT NOT NULL,
                validation_rules TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG soru bankası tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type_id INTEGER NOT NULL,
                difficulty_level TEXT DEFAULT 'medium',
                is_required BOOLEAN DEFAULT 1,
                points INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_type_id) REFERENCES sdg_question_types(id)
            )
        """)
        
        # SDG soru cevapları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                response_text TEXT,
                response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                is_validated BOOLEAN DEFAULT 0,
                validation_notes TEXT,
                FOREIGN KEY (question_id) REFERENCES sdg_question_bank(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # SDG-GRI eşleştirme tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_sdg_gri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_indicator_code TEXT NOT NULL,
                gri_standard TEXT NOT NULL,
                gri_disclosure TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG-TSRS eşleştirme tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_sdg_tsrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_indicator_code TEXT NOT NULL,
                tsrs_section TEXT,
                tsrs_metric TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # GRI-TSRS eşleştirme tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_gri_tsrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gri_standard TEXT NOT NULL,
                gri_disclosure TEXT,
                tsrs_section TEXT,
                tsrs_metric TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG KPI/Metrikler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_kpi_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                kpi_name TEXT NOT NULL,
                metric_description TEXT,
                measurement_frequency TEXT,
                data_source TEXT,
                target_value REAL,
                current_value REAL,
                unit TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG performans metrikleri tablosu
        cursor.execute("""
            CREATE TABLE sdg_performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                measurement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                target_value REAL,
                actual_vs_target REAL,
                improvement_rate REAL,
                benchmark_value REAL,
                industry_percentile REAL,
                calculation_method TEXT,
                data_source TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # SDG veri doğrulama kuralları tablosu
        cursor.execute("""
            CREATE TABLE sdg_validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_description TEXT,
                validation_expression TEXT NOT NULL,
                error_message TEXT,
                severity_level TEXT DEFAULT 'warning',
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SDG veri doğrulama sonuçları tablosu
        cursor.execute("""
            CREATE TABLE sdg_validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                rule_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                validation_status TEXT NOT NULL,
                error_message TEXT,
                suggested_fix TEXT,
                severity_level TEXT,
                FOREIGN KEY (rule_id) REFERENCES sdg_validation_rules(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # SDG veri kalite skorları tablosu
        cursor.execute("""
            CREATE TABLE sdg_data_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                completeness_score REAL DEFAULT 0.0,
                accuracy_score REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,
                timeliness_score REAL DEFAULT 0.0,
                overall_quality_score REAL DEFAULT 0.0,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logging.info("Tablolar olusturuldu")
    
    def load_sdg_goals(self, cursor, df) -> None:
        """SDG hedeflerini yükle"""
        logging.info("SDG hedefleri yukleniyor...")
        
        # Benzersiz SDG hedeflerini al
        goals = df[['Sürdürülebilir Kalkınma Hedefi No:', 'SDG Başlık']].drop_duplicates()
        
        for _, row in goals.iterrows():
            cursor.execute("""
                INSERT INTO sdg_goals (code, title_tr, created_at)
                VALUES (?, ?, ?)
            """, (int(row['Sürdürülebilir Kalkınma Hedefi No:']), 
                  row['SDG Başlık'], datetime.now().isoformat()))
        
        logging.info(f"{len(goals)} SDG hedefi yuklendi")
    
    def load_sdg_targets(self, cursor, df) -> None:
        """Alt hedefleri yükle"""
        logging.info("Alt hedefler yukleniyor...")
        
        # Benzersiz alt hedefleri al
        targets = df[['Sürdürülebilir Kalkınma Hedefi No:', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)']].drop_duplicates()
        
        for _, row in targets.iterrows():
            # SDG hedef ID'sini al
            cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (int(row['Sürdürülebilir Kalkınma Hedefi No:']),))
            goal_result = cursor.fetchone()
            if goal_result:
                goal_id = goal_result[0]
                
                cursor.execute("""
                    INSERT INTO sdg_targets (goal_id, code, title_tr, created_at)
                    VALUES (?, ?, ?, ?)
                """, (goal_id, row['Alt Hedef Kodu'], row['Alt Hedef Tanımı (TR)'], datetime.now().isoformat()))
        
        logging.info(f"{len(targets)} alt hedef yuklendi")
    
    def load_sdg_indicators(self, cursor, df) -> None:
        """Göstergeleri yükle"""
        logging.info("Gostergeler yukleniyor...")
        
        for _, row in df.iterrows():
            # Alt hedef ID'sini al
            cursor.execute("""
                SELECT st.id FROM sdg_targets st
                JOIN sdg_goals sg ON st.goal_id = sg.id
                WHERE sg.code = ? AND st.code = ?
            """, (int(row['Sürdürülebilir Kalkınma Hedefi No:']), row['Alt Hedef Kodu']))
            
            target_result = cursor.fetchone()
            if target_result:
                target_id = target_result[0]
                
                cursor.execute("""
                    INSERT INTO sdg_indicators 
                    (target_id, code, title_tr, data_source, measurement_frequency, 
                     related_sectors, related_funds, kpi_metric, implementation_requirement, 
                     notes, request_status, status, progress_percentage, completeness_percentage,
                     policy_document_exists, data_quality, incentive_readiness_score, 
                     readiness_level, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target_id, row['Gösterge Kodu'], row['Gösterge Tanımı (TR)'],
                    row['Veri Kaynağı'], row['Ölçüm Sıklığı'], row['İlgili Sektörler (Öneri)'],
                    row['İlgili Teşvik / Fon (Örnek)'], row['KPI / Metrik'], row['Uygulama Zorunluluğu'],
                    row['Notlar / Kalanlıklar'], row['Talep Durumu'], row['Durum'],
                    row['İlerleme (%)'], row['Doluluk (%)'], row['Politika/Belge Var mı?'],
                    row['Veri Kalitesi'], row['Teşvik Hazırlık Skoru'], row['Hazırlık Seviyesi'],
                    datetime.now().isoformat()
                ))
        
        logging.info(f"{len(df)} gosterge yuklendi")
    
    def load_sdg_questions(self, cursor, df) -> None:
        """Soruları yükle"""
        logging.info("Sorular yukleniyor...")
        
        # Soru tiplerini oluştur
        question_types = [
            ('Metin', 'Açık uçlu metin sorusu', 'text'),
            ('Sayısal', 'Sayısal değer sorusu', 'numeric'),
            ('Evet/Hayır', 'Evet/Hayır sorusu', 'boolean')
        ]
        
        for type_name, description, input_type in question_types:
            cursor.execute("""
                INSERT OR IGNORE INTO sdg_question_types (type_name, description, input_type)
                VALUES (?, ?, ?)
            """, (type_name, description, input_type))
        
        # Soru bankasını oluştur
        for _, row in df.iterrows():
            sdg_no = int(row['Sürdürülebilir Kalkınma Hedefi No:'])
            indicator_code = row['Gösterge Kodu']
            
            # 3 soru oluştur
            questions = [
                (row['Soru 1'], 'Metin'),
                (row['Soru 2'], 'Sayısal'),
                (row['Soru 3'], 'Evet/Hayır')
            ]
            
            for i, (question_text, question_type) in enumerate(questions, 1):
                if pd.notna(question_text) and str(question_text).strip():
                    # Soru tipi ID'sini al
                    cursor.execute("SELECT id FROM sdg_question_types WHERE type_name = ?", (question_type,))
                    type_result = cursor.fetchone()
                    if type_result:
                        type_id = type_result[0]
                        
                        cursor.execute("""
                            INSERT INTO sdg_question_bank 
                            (sdg_no, indicator_code, question_text, question_type_id, 
                             difficulty_level, is_required, points, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (sdg_no, indicator_code, str(question_text), type_id, 
                              'medium', 1, 1, datetime.now().isoformat()))
        
        logging.info("Sorular yuklendi")
    
    def load_gri_mappings(self, cursor, df) -> None:
        """GRI eşleştirmelerini yükle"""
        logging.info("GRI eslestirmeleri yukleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['GRI Bağlantısı']) and str(row['GRI Bağlantısı']).strip():
                gri_standards = str(row['GRI Bağlantısı']).split(',')
                
                for gri_standard in gri_standards:
                    gri_standard = gri_standard.strip()
                    if gri_standard:
                        cursor.execute("""
                            INSERT INTO map_sdg_gri 
                            (sdg_indicator_code, gri_standard, created_at)
                            VALUES (?, ?, ?)
                        """, (row['Gösterge Kodu'], gri_standard, datetime.now().isoformat()))
        
        logging.info("GRI eslestirmeleri yuklendi")
    
    def load_tsrs_mappings(self, cursor, df) -> None:
        """TSRS eşleştirmelerini yükle"""
        logging.info("TSRS eslestirmeleri yukleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['TSRS Bağlantısı']) and str(row['TSRS Bağlantısı']).strip():
                tsrs_metrics = str(row['TSRS Bağlantısı']).split(',')
                
                for tsrs_metric in tsrs_metrics:
                    tsrs_metric = tsrs_metric.strip()
                    if tsrs_metric:
                        cursor.execute("""
                            INSERT INTO map_sdg_tsrs 
                            (sdg_indicator_code, tsrs_metric, created_at)
                            VALUES (?, ?, ?)
                        """, (row['Gösterge Kodu'], tsrs_metric, datetime.now().isoformat()))
        
        logging.info("TSRS eslestirmeleri yuklendi")
    
    def load_kpi_metrics(self, cursor, df) -> None:
        """KPI/Metrikleri yükle"""
        logging.info("KPI/Metrikler yukleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['KPI / Metrik']) and str(row['KPI / Metrik']).strip():
                cursor.execute("""
                    INSERT INTO sdg_kpi_metrics 
                    (sdg_no, indicator_code, kpi_name, metric_description, 
                     measurement_frequency, data_source, target_value, 
                     current_value, unit, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['Sürdürülebilir Kalkınma Hedefi No:']), row['Gösterge Kodu'], 
                    str(row['KPI / Metrik']), str(row['Gösterge Tanımı (TR)']),
                    row['Ölçüm Sıklığı'], row['Veri Kaynağı'],
                    row.get('Hedef Değer', None), row.get('Mevcut Değer', None),
                    row.get('Birim', None), datetime.now().isoformat()
                ))
        
        logging.info("KPI/Metrikler yuklendi")
    
    def create_csv_files(self, df) -> None:
        """CSV dosyalarını oluştur"""
        logging.info("CSV dosyalari olusturuluyor...")
        
        # SDG-GRI eşleştirme CSV'si
        sdg_gri_data = []
        for _, row in df.iterrows():
            if pd.notna(row['GRI Bağlantısı']) and str(row['GRI Bağlantısı']).strip():
                gri_standards = str(row['GRI Bağlantısı']).split(',')
                for gri_standard in gri_standards:
                    gri_standard = gri_standard.strip()
                    if gri_standard:
                        sdg_gri_data.append({
                            'sdg_indicator_code': row['Gösterge Kodu'],
                            'gri_standard': gri_standard,
                            'gri_disclosure': ''
                        })
        
        if sdg_gri_data:
            pd.DataFrame(sdg_gri_data).to_csv('eslestirme/sdg_gri/samples_sdg_gri.csv', index=False, encoding='utf-8-sig')
            logging.info("SDG-GRI CSV olusturuldu")
        
        # SDG-TSRS eşleştirme CSV'si
        sdg_tsrs_data = []
        for _, row in df.iterrows():
            if pd.notna(row['TSRS Bağlantısı']) and str(row['TSRS Bağlantısı']).strip():
                tsrs_metrics = str(row['TSRS Bağlantısı']).split(',')
                for tsrs_metric in tsrs_metrics:
                    tsrs_metric = tsrs_metric.strip()
                    if tsrs_metric:
                        sdg_tsrs_data.append({
                            'sdg_indicator_code': row['Gösterge Kodu'],
                            'tsrs_section': '',
                            'tsrs_metric': tsrs_metric
                        })
        
        if sdg_tsrs_data:
            pd.DataFrame(sdg_tsrs_data).to_csv('eslestirme/sdg_tsrs/samples_sdg_tsrs.csv', index=False, encoding='utf-8-sig')
            logging.info("SDG-TSRS CSV olusturuldu")
        
        logging.info("CSV dosyalari hazir")

if __name__ == "__main__":
    rebuilder = SystemRebuilder()
    success = rebuilder.rebuild_system()
    if success:
        logging.info("Sistem basariyla yeniden olusturuldu!")
    else:
        logging.info("Sistem olusturma basarisiz!")
