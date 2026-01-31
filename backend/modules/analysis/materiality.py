#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materialite Analizi
Sürdürülebilirlik konularının önceliklendirilmesi
"""

import logging
import os
import sqlite3
from typing import Dict, List


class MaterialityAnalysis:
    """Materialite matrisi ve önceliklendirme"""

    # Sürdürülebilirlik konuları
    TOPICS = {
        'carbon': {'name': 'Karbon Emisyonları', 'category': 'Çevresel'},
        'energy': {'name': 'Enerji Yönetimi', 'category': 'Çevresel'},
        'water': {'name': 'Su Tüketimi', 'category': 'Çevresel'},
        'waste': {'name': 'Atık Yönetimi', 'category': 'Çevresel'},
        'ohs': {'name': 'İş Sağlığı ve Güvenliği', 'category': 'Sosyal'},
        'employment': {'name': 'İstihdam ve İK', 'category': 'Sosyal'},
        'training': {'name': 'Eğitim', 'category': 'Sosyal'},
        'diversity': {'name': 'Çeşitlilik', 'category': 'Sosyal'},
        'economic': {'name': 'Ekonomik Performans', 'category': 'Ekonomik'}
    }

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Materialite tabloları"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materiality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    stakeholder_importance REAL DEFAULT 0,
                    business_impact REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, year, topic)
                )
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"[HATA] Materialite tablo: {e}")
        finally:
            conn.close()

    def set_score(self, company_id: int, year: int, topic: str,
                  stakeholder: float, business: float) -> bool:
        """
        Materialite skoru belirle
        
        Args:
            stakeholder: Paydaş önemi (1-10)
            business: İş etkisi (1-10)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO materiality_scores 
                (company_id, year, topic, stakeholder_importance, business_impact)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(company_id, year, topic) DO UPDATE SET
                    stakeholder_importance=excluded.stakeholder_importance,
                    business_impact=excluded.business_impact
            """, (company_id, year, topic, stakeholder, business))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[HATA] Skor kayit: {e}")
            return False
        finally:
            conn.close()

    def get_matrix(self, company_id: int, year: int) -> List[Dict]:
        """Materialite matrisi al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT topic, stakeholder_importance, business_impact
                FROM materiality_scores
                WHERE company_id=? AND year=?
            """, (company_id, year))

            matrix = []
            for row in cursor.fetchall():
                topic_info = self.TOPICS.get(row[0], {'name': row[0], 'category': 'Diğer'})

                # Öncelik hesapla
                stakeholder = row[1]
                business = row[2]
                priority = self._calculate_priority(stakeholder, business)

                matrix.append({
                    'topic': row[0],
                    'name': topic_info['name'],
                    'category': topic_info['category'],
                    'stakeholder_importance': stakeholder,
                    'business_impact': business,
                    'priority': priority
                })

            # Önceliğe göre sırala
            matrix.sort(key=lambda x: (x['stakeholder_importance'] + x['business_impact']), reverse=True)

            return matrix
        finally:
            conn.close()

    def _calculate_priority(self, stakeholder: float, business: float) -> str:
        """Öncelik seviyesi belirle"""
        avg = (stakeholder + business) / 2

        if stakeholder >= 7 and business >= 7:
            return 'Kritik'
        elif avg >= 7:
            return 'Yüksek'
        elif avg >= 5:
            return 'Orta'
        else:
            return 'Düşük'

    def auto_assess(self, company_id: int, year: int) -> bool:
        """Otomatik değerlendirme (veri bazlı)"""
        # Basitleştirilmiş otomatik skorlama
        default_scores = {
            'carbon': (9, 8),      # Yüksek öncelik
            'energy': (8, 7),
            'ohs': (9, 9),         # Kritik
            'employment': (7, 8),
            'water': (6, 6),
            'waste': (6, 5),
            'training': (7, 6),
            'diversity': (8, 7),
            'economic': (7, 9)
        }

        for topic, (stakeholder, business) in default_scores.items():
            self.set_score(company_id, year, topic, stakeholder, business)

        return True

