#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
SDG Master Veri Yükleme Sistemi
docs/SDG_16_169_232.xlsx dosyasından tüm verileri yükler
"""

import logging
import os
import sqlite3
from datetime import datetime

import pandas as pd
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDGMasterDataLoader:
    """SDG Master veri yükleme sistemi"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.excel_file = os.path.join(base_dir, "docs", "SDG_16_169_232.xlsx")
    
    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def load_master_data(self) -> None:
        """Master verileri yükle"""
        try:
            logging.info("SDG Master verileri yükleniyor...")
            
            # Excel dosyasını oku
            df = pd.read_excel(self.excel_file, sheet_name='MASTER_232')
            logging.info(f"Toplam {len(df)} gösterge yüklendi")
            
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
            
            conn.commit()
            conn.close()
            
            logging.info("Tum veriler basariyla yuklendi!")
            return True
            
        except Exception as e:
            logging.error(f"Veri yuklenirken hata: {e}")
            return False
    
    def load_sdg_goals(self, cursor, df) -> None:
        """SDG hedeflerini yükle"""
        logging.info("SDG hedefleri yükleniyor...")
        
        # Benzersiz SDG hedeflerini al
        goals = df[['SDG No', 'SDG Başlık']].drop_duplicates()
        
        for _, row in goals.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_goals (code, title_tr, created_at)
                VALUES (?, ?, ?)
            """, (int(row['SDG No']), row['SDG Başlık'], datetime.now().isoformat()))
        
        logging.info(f"{len(goals)} SDG hedefi yüklendi")
    
    def load_sdg_targets(self, cursor, df) -> None:
        """Alt hedefleri yükle"""
        logging.info("Alt hedefler yükleniyor...")
        
        # Benzersiz alt hedefleri al
        targets = df[['SDG No', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)']].drop_duplicates()
        
        for _, row in targets.iterrows():
            # SDG hedef ID'sini al
            cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (int(row['SDG No']),))
            goal_result = cursor.fetchone()
            if goal_result:
                goal_id = goal_result[0]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_targets (goal_id, code, title_tr)
                    VALUES (?, ?, ?)
                """, (goal_id, row['Alt Hedef Kodu'], row['Alt Hedef Tanımı (TR)']))
        
        logging.info(f"{len(targets)} alt hedef yüklendi")
    
    def load_sdg_indicators(self, cursor, df) -> None:
        """Göstergeleri yükle"""
        logging.info("Göstergeler yükleniyor...")
        
        for _, row in df.iterrows():
            # Alt hedef ID'sini al
            cursor.execute("""
                SELECT st.id FROM sdg_targets st
                JOIN sdg_goals sg ON st.goal_id = sg.id
                WHERE sg.code = ? AND st.code = ?
            """, (int(row['SDG No']), row['Alt Hedef Kodu']))
            
            target_result = cursor.fetchone()
            if target_result:
                target_id = target_result[0]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_indicators 
                    (target_id, code, title_tr, data_source, measurement_frequency, 
                     related_sectors, related_funds, kpi_metric, implementation_requirement, 
                     notes, request_status, status, progress_percentage, completeness_percentage,
                     policy_document_exists, data_quality, incentive_readiness_score, 
                     readiness_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target_id, row['Gösterge Kodu'], row['Gösterge Tanımı (TR)'],
                    row['Veri Kaynağı'], row['Ölçüm Sıklığı'], row['İlgili Sektörler (Öneri)'],
                    row['İlgili Teşvik / Fon (Örnek)'], row['KPI / Metrik'], row['Uygulama Zorunluluğu'],
                    row['Notlar / Bağımlılıklar'], row['Talep Durumu'], row['Durum'],
                    row['İlerleme (%)'], row['Doluluk (%)'], row['Politika/Belge Var mı?'],
                    row['Veri Kalitesi'], row['Teşvik Hazırlık Skoru'], row['Hazırlık Seviyesi']
                ))
        
        logging.info(f"{len(df)} gösterge yüklendi")
    
    def load_sdg_questions(self, cursor, df) -> None:
        """Soruları yükle"""
        logging.info("Sorular yükleniyor...")
        
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
            sdg_no = int(row['SDG No'])
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
                            INSERT OR REPLACE INTO sdg_question_bank 
                            (sdg_no, indicator_code, question_text, question_type_id, 
                             difficulty_level, is_required, points)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (sdg_no, indicator_code, str(question_text), type_id, 
                              'medium', 1, 1))
        
        logging.info("Sorular yüklendi")
    
    def load_gri_mappings(self, cursor, df) -> None:
        """GRI eşleştirmelerini yükle"""
        logging.info("GRI eşleştirmeleri yükleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['GRI Bağlantısı']) and str(row['GRI Bağlantısı']).strip():
                gri_standards = str(row['GRI Bağlantısı']).split(',')
                
                for gri_standard in gri_standards:
                    gri_standard = gri_standard.strip()
                    if gri_standard:
                        cursor.execute("""
                            INSERT OR REPLACE INTO map_sdg_gri 
                            (sdg_indicator_code, gri_standard)
                            VALUES (?, ?)
                        """, (row['Gösterge Kodu'], gri_standard))
        
        logging.info("GRI eşleştirmeleri yüklendi")
    
    def load_tsrs_mappings(self, cursor, df) -> None:
        """TSRS eşleştirmelerini yükle"""
        logging.info("TSRS eşleştirmeleri yükleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['TSRS Bağlantısı']) and str(row['TSRS Bağlantısı']).strip():
                tsrs_metrics = str(row['TSRS Bağlantısı']).split(',')
                
                for tsrs_metric in tsrs_metrics:
                    tsrs_metric = tsrs_metric.strip()
                    if tsrs_metric:
                        cursor.execute("""
                            INSERT OR REPLACE INTO map_sdg_tsrs 
                            (sdg_indicator_code, tsrs_metric)
                            VALUES (?, ?)
                        """, (row['Gösterge Kodu'], tsrs_metric))
        
        logging.info("TSRS eşleştirmeleri yüklendi")
    
    def load_kpi_metrics(self, cursor, df) -> None:
        """KPI/Metrikleri yükle"""
        logging.info("KPI/Metrikler yükleniyor...")
        
        for _, row in df.iterrows():
            if pd.notna(row['KPI / Metrik']) and str(row['KPI / Metrik']).strip():
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_kpi_metrics 
                    (sdg_no, indicator_code, kpi_name, metric_description, 
                     measurement_frequency, data_source, target_value, 
                     current_value, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['SDG No']), row['Gösterge Kodu'], 
                    str(row['KPI / Metrik']), str(row['Gösterge Tanımı (TR)']),
                    row['Ölçüm Sıklığı'], row['Veri Kaynağı'],
                    row.get('Hedef Değer', None), row.get('Mevcut Değer', None),
                    row.get('Birim', None)
                ))
        
        logging.info("KPI/Metrikler yüklendi")

if __name__ == "__main__":
    loader = SDGMasterDataLoader()
    success = loader.load_master_data()
    if success:
        logging.info("Tum veriler basariyla yuklendi!")
    else:
        logging.info("Veri yukleme basarisiz!")
