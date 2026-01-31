#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
SDG-GRI-TSRS Eşleştirme Modülü
"""

import os
import sqlite3
from typing import Dict, List

import pandas as pd
# from config.database import DB_PATH
DB_PATH = 'sustainage.db'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDGGRIMapping:
    """SDG-GRI-TSRS eşleştirme yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

        # Excel dosyasından veri yükle
        self.excel_data = self.load_excel_data()

    def load_excel_data(self) -> pd.DataFrame:
        """Excel dosyasından SDG verilerini yükle"""
        # Proje kökünden SDG_232.xlsx dosyasını hedefle
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Config'den Excel path al
        try:
            # from config.app_config import get_config
            # config = get_config()
            # excel_path = config.get_excel_path()
            excel_path = os.path.join(base_dir, 'SDG_232.xlsx')
        except Exception:
            # Fallback
            excel_path = os.path.join(base_dir, 'SDG_232.xlsx')

        # Alternatif olarak mutlak konumdaki dosyayı deneyelim
        if not os.path.exists(excel_path):
             logging.info(f"Excel dosyası bulunamadı: {excel_path}")
             return pd.DataFrame()

        # Öncelikle MASTER_232 sayfasını okumayı dene, olmazsa varsayılanı dene
        try:
            df = pd.read_excel(excel_path, sheet_name='MASTER_232')
        except Exception:
            try:
                df = pd.read_excel(excel_path)
            except Exception as e2:
                logging.error(f"Excel dosyası okunurken hata: {e2}")
                return pd.DataFrame()

        # Kolon adlarını normalize et
        df = self._normalize_excel_columns(df)

        logging.info(f"Excel verisi yüklendi: {len(df)} gösterge")
        return df

    def _find_col(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for c in candidates:
            if c in df.columns:
                return c
        return ''

    def _normalize_excel_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Excel kolonlarını dahili standart isimlere eşle"""
        if df.empty:
            return df

        # Olası kolon eş adayları
        mapping_candidates = {
            'SDG No': [
                'SDG No', 'Sürdürülebilir Kalkınma Hedefi No:', 'Hedef No', 'Goal No', 'SDG',
                'Srdrlebilir Kalknma Hedefi No:'  # Encoding sorunu için
            ],
            'SDG Başlık': [
                'SDG Başlık', 'SDG Title', 'Goal Title'
            ],
            'Alt Hedef Kodu': [
                'Alt Hedef Kodu', 'Target Code'
            ],
            'Alt Hedef Tanımı (TR)': [
                'Alt Hedef Tanımı (TR)', 'Alt Hedef Tanımı', 'Target Description (TR)'
            ],
            'Gösterge Kodu': [
                'Gösterge Kodu', 'Indicator Code'
            ],
            'Gösterge Tanımı (TR)': [
                'Gösterge Tanımı (TR)', 'Indicator Description (TR)', 'Gösterge Tanımı'
            ],
            'GRI Bağlantısı': [
                'GRI Bağlantısı', 'GRI', 'GRI Connections'
            ],
            'TSRS Bağlantısı': [
                'TSRS Bağlantısı', 'TSRS', 'TSRS Connections'
            ],
            'Sorumlu Birim/Kişi': [
                'Sorumlu Birim/Kişi', 'Sorumlu', 'Responsible Unit/Person'
            ],
            'Veri Kaynağı': [
                'Veri Kaynağı', 'Data Source'
            ],
            'Ölçüm Sıklığı': [
                'Ölçüm Sıklığı', 'Measurement Frequency'
            ],
            'Soru 1': [
                'Soru 1', 'Question 1'
            ],
            'Soru 2': [
                'Soru 2', 'Question 2'
            ],
            'Soru 3': [
                'Soru 3', 'Question 3'
            ]
        }

        rename_map = {}
        for canon, candidates in mapping_candidates.items():
            found = self._find_col(df, candidates)
            if found and found != canon:
                rename_map[found] = canon

        # Özel durum: SDG No kolonu için encoding sorunu olabilir
        if 'SDG No' not in df.columns:
            for col in df.columns:
                # Encoding sorunu olan kolon adlarını kontrol et
                col_lower = col.lower()
                if (('sürdürülebilir' in col_lower or 'srdrlebilir' in col_lower) and
                    ('kalkınma' in col_lower or 'kalknma' in col_lower) and
                    ('hedefi' in col_lower or 'hedef' in col_lower) and
                    ('no' in col_lower) and ':' in col):
                    rename_map[col] = 'SDG No'
                    logging.info(f"SDG No kolonu bulundu ve yeniden adlandırıldı: {col} -> SDG No")
                    break

        if rename_map:
            df = df.rename(columns=rename_map)

        # SDG No değerini sayısal hale getir
        if 'SDG No' in df.columns:
            try:
                df['SDG No'] = pd.to_numeric(df['SDG No'], errors='coerce').astype('Int64')
            except Exception as e:
                logging.error(f'Silent error in sdg_gri_mapping.py: {str(e)}')

        return df

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def get_indicators_for_selected_goals(self, selected_goal_ids: List[int]) -> pd.DataFrame:
        """Seçilen SDG hedefleri için gösterge ve soruları getir"""
        if self.excel_data.empty:
            return pd.DataFrame()

        # Seçilen SDG hedeflerine ait göstergeleri filtrele
        sdg_col = 'SDG No' if 'SDG No' in self.excel_data.columns else ''
        if not sdg_col:
            # En azından bir eş başlık bulmayı dene
            sdg_col = self._find_col(self.excel_data, ['Sürdürülebilir Kalkınma Hedefi No:', 'Hedef No', 'Goal No', 'SDG'])
        if not sdg_col:
            logging.error("Excel veri hatası: SDG kolonunu bulamadım")
            return pd.DataFrame()
        filtered_data = self.excel_data[self.excel_data[sdg_col].isin(selected_goal_ids)].copy()

        return filtered_data

    def get_questions_for_goals(self, selected_goal_ids: List[int]) -> List[Dict]:
        """Seçilen hedefler için soruları getir"""
        indicators = self.get_indicators_for_selected_goals(selected_goal_ids)

        questions = []
        for _, row in indicators.iterrows():
            # Her gösterge için 3 soru
            for i in range(1, 4):
                question_col = f'Soru {i}' if f'Soru {i}' in indicators.columns else f'Question {i}'
                val = row.get(question_col)
                if pd.notna(val) and str(val).strip():
                    questions.append({
                        'sdg_no': int(row.get('SDG No')) if pd.notna(row.get('SDG No')) else None,
                        'sdg_title': row.get('SDG Başlık', ''),
                        'target_code': row.get('Alt Hedef Kodu', ''),
                        'target_title': row.get('Alt Hedef Tanımı (TR)', ''),
                        'indicator_code': row.get('Gösterge Kodu', ''),
                        'indicator_title': row.get('Gösterge Tanımı (TR)', ''),
                        'question_number': i,
                        'question_text': val,
                        'gri_connection': row.get('GRI Bağlantısı') if pd.notna(row.get('GRI Bağlantısı')) else '',
                        'tsrs_connection': row.get('TSRS Bağlantısı') if pd.notna(row.get('TSRS Bağlantısı')) else '',
                        'responsible_unit': row.get('Sorumlu Birim/Kişi') if pd.notna(row.get('Sorumlu Birim/Kişi')) else '',
                        'data_source': row.get('Veri Kaynağı') if pd.notna(row.get('Veri Kaynağı')) else '',
                        'measurement_frequency': row.get('Ölçüm Sıklığı') if pd.notna(row.get('Ölçüm Sıklığı')) else ''
                    })

        return questions

    def get_total_questions_count(self, selected_goal_ids: List[int]) -> int:
        """Seçilen hedefler için toplam soru sayısını getir"""
        questions = self.get_questions_for_goals(selected_goal_ids)
        return len(questions)

    def get_gri_mapping_for_goals(self, selected_goal_ids: List[int]) -> Dict:
        """Seçilen hedefler için GRI eşleştirmelerini getir"""
        indicators = self.get_indicators_for_selected_goals(selected_goal_ids)

        gri_mapping = {}

        for _, row in indicators.iterrows():
            sdg_no_val = row.get('SDG No')
            try:
                sdg_no = int(sdg_no_val) if pd.notna(sdg_no_val) else None
            except Exception:
                sdg_no = None
            gri_connection = row.get('GRI Bağlantısı') if pd.notna(row.get('GRI Bağlantısı')) else ''
            tsrs_connection = row.get('TSRS Bağlantısı') if pd.notna(row.get('TSRS Bağlantısı')) else ''

            if sdg_no is None:
                continue
            if sdg_no not in gri_mapping:
                gri_mapping[sdg_no] = {
                    'sdg_title': row.get('SDG Başlık', ''),
                    'indicators': [],
                    'gri_standards': set(),
                    'tsrs_standards': set()
                }

            gri_mapping[sdg_no]['indicators'].append({
                'indicator_code': row.get('Gösterge Kodu', ''),
                'indicator_title': row.get('Gösterge Tanımı (TR)', ''),
                'target_code': row.get('Alt Hedef Kodu', ''),
                'target_title': row.get('Alt Hedef Tanımı (TR)', ''),
                'gri_connection': gri_connection,
                'tsrs_connection': tsrs_connection
            })

            if gri_connection:
                gri_mapping[sdg_no]['gri_standards'].add(gri_connection)
            if tsrs_connection:
                gri_mapping[sdg_no]['tsrs_standards'].add(tsrs_connection)

        # Set'leri list'e çevir
        for sdg_no in gri_mapping:
            gri_mapping[sdg_no]['gri_standards'] = list(gri_mapping[sdg_no]['gri_standards'])
            gri_mapping[sdg_no]['tsrs_standards'] = list(gri_mapping[sdg_no]['tsrs_standards'])

        return gri_mapping

    def save_question_responses(self, company_id: int, responses: List[Dict]) -> bool:
        """Soru yanıtlarını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce mevcut yanıtları sil
            cursor.execute("""
                DELETE FROM sdg_question_responses 
                WHERE company_id = ?
            """, (company_id,))

            # Yeni yanıtları ekle
            for response in responses:
                cursor.execute("""
                    INSERT INTO sdg_question_responses 
                    (company_id, sdg_no, indicator_code, question_number, question_text, 
                     answer_text, answer_date, gri_connection, tsrs_connection)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    response['sdg_no'],
                    response['indicator_code'],
                    response['question_number'],
                    response['question_text'],
                    response['answer_text'],
                    response['answered_at'],
                    response['gri_connection'],
                    response['tsrs_connection']
                ))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Soru yanıtları kaydedilirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_answered_questions_count(self, company_id: int, selected_goal_ids: List[int]) -> int:
        """Cevaplanan soru sayısını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_question_responses 
                WHERE company_id = ? AND sdg_no IN ({})
            """.format(','.join('?' * len(selected_goal_ids))),
            [company_id] + selected_goal_ids)

            return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Cevaplanan soru sayısı getirilirken hata: {e}")
            return 0
        finally:
            conn.close()

    def get_answer_percentage(self, company_id: int, selected_goal_ids: List[int]) -> float:
        """Yanıt yüzdesini hesapla"""
        total_questions = self.get_total_questions_count(selected_goal_ids)
        if total_questions == 0:
            return 0.0

        answered_questions = self.get_answered_questions_count(company_id, selected_goal_ids)
        return (answered_questions / total_questions) * 100

    def get_selected_sdg_goals(self, company_id: int) -> List[int]:
        """Şirket için seçilen SDG hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT goal_id FROM user_sdg_selections 
                WHERE company_id = ?
            """, (company_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Seçilen SDG hedefleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_sdg_indicators_for_goals(self, goal_ids: List[int]) -> List[str]:
        """Seçilen SDG hedefleri için gösterge kodlarını getir"""
        if not goal_ids:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            placeholders = ','.join('?' * len(goal_ids))
            cursor.execute(f"""
                SELECT DISTINCT si.code 
                FROM sdg_indicators si
                JOIN sdg_targets st ON si.target_id = st.id
                WHERE st.goal_id IN ({placeholders})
            """, goal_ids)

            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"SDG gösterge kodları getirilirken hata: {e}")
            return []
        finally:
            conn.close()
