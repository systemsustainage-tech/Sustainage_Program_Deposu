#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı Veri Yükleme - SDG_232.xlsx'den verileri yükler
"""

import logging
import sqlite3
import os
from datetime import datetime
import pandas as pd
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data() -> None:
    """Verileri hızlıca yükle"""
    try:
        logging.info("Veriler yukleniyor...")
        
        # Excel dosyasını oku
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excel_path = os.path.join(base_dir, "SDG_232.xlsx")
        df = pd.read_excel(excel_path, sheet_name='MASTER_232')
        logging.info(f"Toplam {len(df)} gosterge yuklendi")
        
        # Veritabanına bağlan
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # SDG hedeflerini yükle
        goals = df[['Sürdürülebilir Kalkınma Hedefi No:', 'SDG Başlık']].drop_duplicates()
        for _, row in goals.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_goals (code, title_tr, created_at)
                VALUES (?, ?, ?)
            """, (int(row['Sürdürülebilir Kalkınma Hedefi No:']), 
                  row['SDG Başlık'], datetime.now().isoformat()))
        logging.info(f"{len(goals)} SDG hedefi yuklendi")
        
        # Alt hedefleri yükle
        targets = df[['Sürdürülebilir Kalkınma Hedefi No:', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)']].drop_duplicates()
        for _, row in targets.iterrows():
            cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (int(row['Sürdürülebilir Kalkınma Hedefi No:']),))
            goal_result = cursor.fetchone()
            if goal_result:
                goal_id = goal_result[0]
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_targets (goal_id, code, title_tr, created_at)
                    VALUES (?, ?, ?, ?)
                """, (goal_id, row['Alt Hedef Kodu'], row['Alt Hedef Tanımı (TR)'], datetime.now().isoformat()))
        logging.info(f"{len(targets)} alt hedef yuklendi")
        
        # Göstergeleri yükle
        for _, row in df.iterrows():
            cursor.execute("""
                SELECT st.id FROM sdg_targets st
                JOIN sdg_goals sg ON st.goal_id = sg.id
                WHERE sg.code = ? AND st.code = ?
            """, (int(row['Sürdürülebilir Kalkınma Hedefi No:']), row['Alt Hedef Kodu']))
            
            target_result = cursor.fetchone()
            if target_result:
                target_id = target_result[0]
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_indicators 
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
        
        conn.commit()
        conn.close()
        
        logging.info("Tum veriler basariyla yuklendi!")
        return True
        
    except Exception as e:
        logging.error(f"Veri yuklenirken hata: {e}")
        return False

if __name__ == "__main__":
    success = load_data()
    if success:
        logging.info("Veriler hazir!")
    else:
        logging.info("Veri yukleme basarisiz!")
