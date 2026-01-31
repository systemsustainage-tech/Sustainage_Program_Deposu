import logging
import argparse
import os
import sqlite3

import pandas as pd
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_sdg_complete_data(db_path: str = DB_PATH) -> None:
    """SDG_232_TURKCE_MASTER_WITH_QUESTIONS_EXACT.xlsx dosyasını veritabanına aktar"""
    
    # Veritabanına bağlan
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel('docs/SDG_232_TURKCE_MASTER_WITH_QUESTIONS_EXACT.xlsx')
        logging.info(f"Excel dosyasi okundu: {len(df)} satir")
        
        # SDG hedeflerini ekle
        sdg_goals = df[['SDG No', 'SDG Başlık']].drop_duplicates()
        logging.info(f"SDG hedef sayisi: {len(sdg_goals)}")
        
        for _, row in sdg_goals.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_goals (code, title_tr)
                VALUES (?, ?)
            """, (int(row['SDG No']), str(row['SDG Başlık'])))
        
        # SDG hedeflerini al
        cursor.execute("SELECT id, code FROM sdg_goals")
        goals = {code: id for id, code in cursor.fetchall()}
        
        # Alt hedefleri ekle
        targets = df[['SDG No', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)']].drop_duplicates()
        logging.info(f"Alt hedef sayisi: {len(targets)}")
        
        for _, row in targets.iterrows():
            if pd.notna(row['Alt Hedef Kodu']) and pd.notna(row['Alt Hedef Tanımı (TR)']):
                goal_id = goals.get(int(row['SDG No']))
                if goal_id:
                    cursor.execute("""
                        INSERT OR REPLACE INTO sdg_targets (goal_id, code, title_tr)
                        VALUES (?, ?, ?)
                    """, (goal_id, str(row['Alt Hedef Kodu']), str(row['Alt Hedef Tanımı (TR)'])))
        
        # Alt hedefleri al
        cursor.execute("SELECT id, goal_id, code FROM sdg_targets")
        targets_dict = {}
        for id, goal_id, code in cursor.fetchall():
            targets_dict[(goal_id, code)] = id
        
        # Göstergeleri ekle
        logging.info(f"Gosterge sayisi: {len(df)}")
        
        for _, row in df.iterrows():
            if pd.notna(row['Gösterge Kodu']) and pd.notna(row['Gösterge Tanımı (TR)']):
                goal_id = goals.get(int(row['SDG No']))
                target_id = targets_dict.get((goal_id, str(row['Alt Hedef Kodu'])))
                
                if target_id:
                    # Soru bankasına ekle
                    cursor.execute("""
                        INSERT OR REPLACE INTO question_bank 
                        (indicator_code, q1, q2, q3, default_unit, default_frequency, default_owner, default_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row['Gösterge Kodu']),
                        str(row['Soru 1']) if pd.notna(row['Soru 1']) else None,
                        str(row['Soru 2']) if pd.notna(row['Soru 2']) else None,
                        str(row['Soru 3']) if pd.notna(row['Soru 3']) else None,
                        str(row['KPI / Metrik']) if pd.notna(row['KPI / Metrik']) else None,
                        str(row['Ölçüm Sıklığı']) if pd.notna(row['Ölçüm Sıklığı']) else 'Yıllık',
                        str(row['Sorumlu Birim/Kişi']) if pd.notna(row['Sorumlu Birim/Kişi']) else None,
                        str(row['Veri Kaynağı']) if pd.notna(row['Veri Kaynağı']) else None
                    ))
                    
                    # SDG göstergesini ekle
                    cursor.execute("""
                        INSERT OR REPLACE INTO sdg_indicators 
                        (target_id, code, title_tr, unit, frequency, topic)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        target_id,
                        str(row['Gösterge Kodu']),
                        str(row['Gösterge Tanımı (TR)']),
                        str(row['KPI / Metrik']) if pd.notna(row['KPI / Metrik']) else None,
                        str(row['Ölçüm Sıklığı']) if pd.notna(row['Ölçüm Sıklığı']) else 'Yıllık',
                        'genel'  # Varsayılan topic
                    ))
        
        conn.commit()
        logging.info("SDG verileri basariyla aktarildi! DB:", os.path.abspath(db_path))
        
        # İstatistikleri göster
        cursor.execute("SELECT COUNT(*) FROM sdg_goals")
        goals_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sdg_targets")
        targets_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sdg_indicators")
        indicators_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM question_bank")
        questions_count = cursor.fetchone()[0]
        
        logging.info("\nVeritabani istatistikleri:")
        logging.info(f"  SDG Hedefleri: {goals_count}")
        logging.info(f"  Alt Hedefler: {targets_count}")
        logging.info(f"  Gostergeler: {indicators_count}")
        logging.info(f"  Soru Bankasi: {questions_count}")
        
    except Exception as e:
        logging.error(f"Hata: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SDG master Excel'i veritabanına aktar")
    parser.add_argument('--db', default=DB_PATH, help='SQLite veritabanı yolu')
    args = parser.parse_args()
    import_sdg_complete_data(args.db)

