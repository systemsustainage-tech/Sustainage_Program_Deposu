import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Veri Toplama Sistemi
Her SDG göstergesi için 3 soru sistemi
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import pandas as pd

from config.settings import ensure_directories, get_db_path


class SDGDataCollection:
    """SDG veri toplama sistemi"""

    def __init__(self, db_path: str | None = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            ensure_directories()
            self.db_path = get_db_path()

        self.questions_df = self._load_questions_excel()
        self._create_tables()

    def _load_questions_excel(self) -> pd.DataFrame:
        """Soru bankası Excel dosyasını yükle (MASTER_232 sayfası)"""
        try:
            # Proje kökünden SDG_232.xlsx yolunu hedefle
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            # Config'den Excel path al
            try:
                from config.app_config import get_config
                config = cast(Any, get_config())
                excel_path = config.get_excel_path()
            except Exception:
                # Fallback
                excel_path = os.path.join(base_dir, 'SDG_232.xlsx')

            # Doğrudan mutlak yol varsa onu kullan
            abs_path = excel_path
            
            # MASTER_232 sayfasını oku
            df = pd.read_excel(abs_path, sheet_name='MASTER_232')

            # Beklenen sütunların varlığını garanti etmek için esnek normalizasyon
            # Olası alternatif isimleri kanonik isimlere eşle
            alt_names = {
                'SDG No': ['SDG No', 'sdg_no', 'SDG_No', 'SDGNo', 'SDG No.', 'SDG No '],
                'SDG Başlık': ['SDG Başlık', 'SDG Başlığı', 'SDG Baslik', 'sdg_title'],
                'Alt Hedef Kodu': ['Alt Hedef Kodu', 'AltHedefKodu', 'target_code', 'Alt Hedef Kodu '],
                'Alt Hedef Tanımı (TR)': ['Alt Hedef Tanımı (TR)', 'Alt Hedef Tanımı', 'target_title_tr', 'Alt Hedef Tanimi (TR)'],
                'Gösterge Kodu': ['Gösterge Kodu', 'indicator_code', 'Indicator Code', 'Gösterge'],
                'Gösterge Tanımı (TR)': ['Gösterge Tanımı (TR)', 'Gösterge Tanımı', 'title_tr', 'Indicator Title (TR)']
            }

            # Mevcut kolonları küçük harfe indirip kıyas için hazırlayalım
            existing_cols = list(df.columns)
            lower_map = {c.lower().strip(): c for c in existing_cols}

            for canonical, alternatives in alt_names.items():
                if canonical not in df.columns:
                    # Alternatiflerden mevcut olanı bul ve yeniden adlandır
                    found = None
                    for alt in alternatives:
                        key = alt.lower().strip()
                        if key in lower_map:
                            found = lower_map[key]
                            break
                    if found:
                        df.rename(columns={found: canonical}, inplace=True)

            # Eğer hâlâ 'SDG No' yoksa, türetmeyi dene (Gösterge/Alt Hedef Kodu üzerinden)
            if 'SDG No' not in df.columns:
                try:
                    if 'Gösterge Kodu' in df.columns:
                        df['SDG No'] = df['Gösterge Kodu'].astype(str).str.extract(r'^(\d+)')[0].astype(int)
                    elif 'Alt Hedef Kodu' in df.columns:
                        df['SDG No'] = df['Alt Hedef Kodu'].astype(str).str.extract(r'^(\d+)')[0].astype(int)
                except Exception as e:
                    # Türetemezsek bırak; aşağıdaki kontrol uyarı verecek
                    logging.error(f"Silent error caught: {str(e)}")

            required_cols = ['SDG No', 'SDG Başlık', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)',
                              'Gösterge Kodu', 'Gösterge Tanımı (TR)']
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                # Eksikleri bildir ama çalışmaya devam etmek için boş DataFrame dönme yerine
                # minimum alanlar yoksa sistemi boş veriyle başlat
                # raise ValueError(f"MASTER_232 sayfasında eksik sütunlar: {missing}")
                logging.error(f"MASTER_232 sayfasında eksik sütunlar: {missing}")
                return pd.DataFrame()

            logging.info(f"MASTER_232 yüklendi: {len(df)} satır")
            return df
        except Exception as e:
            logging.error(f"Soru bankası (MASTER_232) yüklenirken hata: {e}")
            return pd.DataFrame()

    def _create_tables(self) -> None:
        """Veri toplama tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SDG soru yanıtları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_number INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT,
                answer_value REAL,
                answer_boolean BOOLEAN,
                answer_date TEXT,
                responsible_unit TEXT,
                data_source TEXT,
                data_method TEXT,
                measurement_frequency TEXT,
                related_sectors TEXT,
                related_funds TEXT,
                kpi_metric TEXT,
                gri_connection TEXT,
                tsrs_connection TEXT,
                implementation_requirement TEXT,
                data_quality TEXT,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                progress_percentage REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG gösterge durumu tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_indicator_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                target_code TEXT NOT NULL,
                target_title TEXT NOT NULL,
                question_1_answered BOOLEAN DEFAULT FALSE,
                question_2_answered BOOLEAN DEFAULT FALSE,
                question_3_answered BOOLEAN DEFAULT FALSE,
                total_questions INTEGER DEFAULT 3,
                answered_questions INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()
        logging.info("SDG veri toplama tabloları oluşturuldu")

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def get_questions_for_indicator(self, indicator_code: str) -> List[Dict]:
        """Belirli bir gösterge için soruları getir"""
        if self.questions_df.empty:
            return []

        # Gösterge koduna göre filtrele
        indicator_data = self.questions_df[self.questions_df['Gösterge Kodu'] == indicator_code]

        if indicator_data.empty:
            return []

        row = indicator_data.iloc[0]

        questions = []
        for i in range(1, 4):  # Soru 1, 2, 3
            question_text = row.get(f'Soru {i}')
            if pd.notna(question_text) and question_text.strip():
                questions.append({
                    'question_number': i,
                    'question_text': str(question_text).strip(),
                    'responsible_unit': str(row.get('Sorumlu Birim/Kişi', '')),
                    'data_source': str(row.get('Veri Kaynağı', '')),
                    'data_method': str(row.get('Veri Yöntemi', '')),
                    'measurement_frequency': str(row.get('Ölçüm Sıklığı', '')),
                    'related_sectors': str(row.get('İlgili Sektörler (Öneri)', '')),
                    'related_funds': str(row.get('İlgili Teşvik / Fon (Örnek)', '')),
                    'kpi_metric': str(row.get('KPI / Metrik', '')),
                    'gri_connection': str(row.get('GRI Bağlantısı', '')),
                    'tsrs_connection': str(row.get('TSRS Bağlantısı', '')),
                    'implementation_requirement': str(row.get('Uygulama Zorunluluğu', '')),
                    'data_quality': str(row.get('Veri Kalitesi', '')),
                    'notes': str(row.get('Notlar / Bağımlılıklar', ''))
                })

        return questions

    def get_questions_for_company(self, company_id: int, sdg_no: Optional[int] = None) -> List[Dict]:
        """Şirket için soruları getir (SDG'ye göre filtreleme opsiyonel)"""
        if self.questions_df.empty:
            return []

        # SDG numarasına göre filtrele
        if sdg_no:
            filtered_df = self.questions_df[self.questions_df['SDG No'] == sdg_no]
        else:
            filtered_df = self.questions_df

        questions = []
        for _, row in filtered_df.iterrows():
            indicator_code = row['Gösterge Kodu']
            indicator_title = row['Gösterge Tanımı (TR)']
            target_code = row['Alt Hedef Kodu']
            target_title = row['Alt Hedef Tanımı (TR)']

            # Bu gösterge için soruları al
            indicator_questions = self.get_questions_for_indicator(indicator_code)

            questions.append({
                'sdg_no': int(row['SDG No']),
                'sdg_title': row['SDG Başlık'],
                'target_code': target_code,
                'target_title': target_title,
                'indicator_code': indicator_code,
                'indicator_title': indicator_title,
                'questions': indicator_questions
            })

        return questions

    def save_answer(self, company_id: int, indicator_code: str, question_number: int,
                   answer_text: str | None = None, answer_value: float | None = None,
                   answer_boolean: bool | None = None, **kwargs) -> bool:
        """Soru yanıtını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Soru metnini al
            question_text = ""
            if not self.questions_df.empty:
                indicator_data = self.questions_df[self.questions_df['Gösterge Kodu'] == indicator_code]
                if not indicator_data.empty:
                    question_text = str(indicator_data.iloc[0].get(f'Soru {question_number}', ''))

            # SDG numarasını al
            sdg_no = None
            if not self.questions_df.empty:
                indicator_data = self.questions_df[self.questions_df['Gösterge Kodu'] == indicator_code]
                if not indicator_data.empty:
                    sdg_no = int(indicator_data.iloc[0]['SDG No'])

            # Mevcut yanıtı kontrol et
            cursor.execute("""
                SELECT id FROM sdg_question_responses 
                WHERE company_id = ? AND indicator_code = ? AND question_number = ?
            """, (company_id, indicator_code, question_number))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute("""
                    UPDATE sdg_question_responses 
                    SET answer_text = ?, answer_value = ?, answer_boolean = ?, 
                        answer_date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (answer_text, answer_value, answer_boolean,
                      datetime.now().isoformat(), existing[0]))
            else:
                # Yeni kayıt oluştur
                cursor.execute("""
                    INSERT INTO sdg_question_responses 
                    (company_id, sdg_no, indicator_code, question_number, question_text,
                     answer_text, answer_value, answer_boolean, answer_date,
                     responsible_unit, data_source, data_method, measurement_frequency,
                     related_sectors, related_funds, kpi_metric, gri_connection,
                     tsrs_connection, implementation_requirement, data_quality, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, sdg_no, indicator_code, question_number, question_text,
                    answer_text, answer_value, answer_boolean, datetime.now().isoformat(),
                    kwargs.get('responsible_unit', ''),
                    kwargs.get('data_source', ''),
                    kwargs.get('data_method', ''),
                    kwargs.get('measurement_frequency', ''),
                    kwargs.get('related_sectors', ''),
                    kwargs.get('related_funds', ''),
                    kwargs.get('kpi_metric', ''),
                    kwargs.get('gri_connection', ''),
                    kwargs.get('tsrs_connection', ''),
                    kwargs.get('implementation_requirement', ''),
                    kwargs.get('data_quality', ''),
                    kwargs.get('notes', '')
                ))

            # Gösterge durumunu güncelle
            self._update_indicator_status(company_id, indicator_code)

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Soru yanıtı kaydedilirken hata: {e}")
            return False
        finally:
            conn.close()

    def _update_indicator_status(self, company_id: int, indicator_code: str) -> None:
        """Gösterge durumunu güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Yanıtlanan soru sayısını hesapla
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_question_responses 
                WHERE company_id = ? AND indicator_code = ? 
                AND (answer_text IS NOT NULL OR answer_value IS NOT NULL OR answer_boolean IS NOT NULL)
            """, (company_id, indicator_code))

            answered_count = cursor.fetchone()[0]

            # Gösterge bilgilerini al
            if not self.questions_df.empty:
                indicator_data = self.questions_df[self.questions_df['Gösterge Kodu'] == indicator_code]
                if not indicator_data.empty:
                    row = indicator_data.iloc[0]
                    sdg_no = int(row['SDG No'])
                    indicator_title = row['Gösterge Tanımı (TR)']
                    target_code = row['Alt Hedef Kodu']
                    target_title = row['Alt Hedef Tanımı (TR)']

                    # Gösterge durumunu güncelle veya oluştur
                    cursor.execute("""
                        INSERT OR REPLACE INTO sdg_indicator_status 
                        (company_id, sdg_no, indicator_code, indicator_title, target_code, target_title,
                         question_1_answered, question_2_answered, question_3_answered,
                         total_questions, answered_questions, completion_percentage, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        company_id, sdg_no, indicator_code, indicator_title, target_code, target_title,
                        answered_count >= 1, answered_count >= 2, answered_count >= 3,
                        3, answered_count, (answered_count / 3) * 100
                    ))

            conn.commit()

        except Exception as e:
            logging.error(f"Gösterge durumu güncellenirken hata: {e}")
        finally:
            conn.close()

    def get_company_progress(self, company_id: int, sdg_no: Optional[int] = None) -> Dict:
        """Şirket ilerlemesini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if sdg_no:
                cursor.execute("""
                    SELECT sdg_no, COUNT(*) as total_indicators,
                           SUM(answered_questions) as total_answered,
                           SUM(total_questions) as total_questions,
                           AVG(completion_percentage) as avg_completion
                    FROM sdg_indicator_status 
                    WHERE company_id = ? AND sdg_no = ?
                    GROUP BY sdg_no
                """, (company_id, sdg_no))
            else:
                cursor.execute("""
                    SELECT COUNT(DISTINCT indicator_code) as total_indicators,
                           SUM(answered_questions) as total_answered,
                           SUM(total_questions) as total_questions,
                           AVG(completion_percentage) as avg_completion
                    FROM sdg_indicator_status 
                    WHERE company_id = ?
                """, (company_id,))

            result = cursor.fetchone()

            if result:
                # SUM/AVG boş sonuçta None dönebilir; güvenli varsayılanlar uygulayalım
                total_indicators = int(result[0] or 0)
                total_answered = int(result[1] or 0)
                total_questions = int(result[2] or 0)
                avg_completion = float(result[3] or 0.0)
                remaining = max(total_questions - total_answered, 0)

                return {
                    'total_indicators': total_indicators,
                    'total_questions': total_questions,
                    'answered_questions': total_answered,
                    'completion_percentage': avg_completion,
                    'remaining_questions': remaining
                }
            else:
                return {
                    'total_indicators': 0,
                    'total_questions': 0,
                    'answered_questions': 0,
                    'completion_percentage': 0.0,
                    'remaining_questions': 0
                }

        except Exception as e:
            logging.error(f"İlerleme bilgisi getirilirken hata: {e}")
            return {
                'total_indicators': 0,
                'total_questions': 0,
                'answered_questions': 0,
                'completion_percentage': 0.0,
                'remaining_questions': 0
            }
        finally:
            conn.close()

    def get_indicator_responses(self, company_id: int, indicator_code: str) -> List[Dict]:
        """Gösterge yanıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT question_number, question_text, answer_text, answer_value, 
                       answer_boolean, answer_date, responsible_unit, data_source,
                       data_method, measurement_frequency, related_sectors,
                       related_funds, kpi_metric, gri_connection, tsrs_connection,
                       implementation_requirement, data_quality, notes, status
                FROM sdg_question_responses 
                WHERE company_id = ? AND indicator_code = ?
                ORDER BY question_number
            """, (company_id, indicator_code))

            responses = []
            for row in cursor.fetchall():
                responses.append({
                    'question_number': row[0],
                    'question_text': row[1],
                    'answer_text': row[2],
                    'answer_value': row[3],
                    'answer_boolean': row[4],
                    'answer_date': row[5],
                    'responsible_unit': row[6],
                    'data_source': row[7],
                    'data_method': row[8],
                    'measurement_frequency': row[9],
                    'related_sectors': row[10],
                    'related_funds': row[11],
                    'kpi_metric': row[12],
                    'gri_connection': row[13],
                    'tsrs_connection': row[14],
                    'implementation_requirement': row[15],
                    'data_quality': row[16],
                    'notes': row[17],
                    'status': row[18]
                })

            return responses

        except Exception as e:
            logging.error(f"Gösterge yanıtları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

if __name__ == "__main__":
    # Test
    data_collection = SDGDataCollection()
    logging.info("SDG Veri Toplama Sistemi başlatıldı")

    # Test soruları
    questions = data_collection.get_questions_for_company(1, 9)
    logging.info(f"SDG 9 için {len(questions)} gösterge bulundu")

    if questions:
        first_indicator = questions[0]
        logging.info(f"İlk gösterge: {first_indicator['indicator_code']}")
        logging.info(f"Soru sayısı: {len(first_indicator['questions'])}")
