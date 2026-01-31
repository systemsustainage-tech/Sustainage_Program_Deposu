#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG bonus tohumlama aracı:
- SDG soru yanıtları (sdg_question_responses) içine örnek yanıtlar ekler
- TSRS materyalite değerlendirmesi (tsrs_materiality_assessment) içine örnek kayıtlar ekler

Kullanım:
  python tools/seed_esg_bonuses.py --db data/sdg_desktop.sqlite --company 1 --period 2025
"""

import logging
import argparse
import sqlite3
from typing import List, Tuple
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def table_columns(cur, table: str) -> List[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def seed_sdg_question_responses(conn: sqlite3.Connection, company_id: int, period: str) -> int:
    cur = conn.cursor()
    cols = set(table_columns(cur, 'sdg_question_responses'))

    # Kullanılacak göstergeler (DB'de mevcut olanlardan örnek)
    sample_indicators = ['7.2.1', '13.2.2', '8.5.1']
    inserted = 0

    if {'company_id', 'sdg_no', 'indicator_code', 'question_number', 'question_text', 'answer_text', 'answer_value'}.issubset(cols):
        for code in sample_indicators:
            try:
                sdg_no = int(code.split('.')[0])
                cur.execute(
                    """
                    INSERT INTO sdg_question_responses(
                        company_id, sdg_no, indicator_code, question_number, question_text,
                        answer_text, answer_value, measurement_frequency, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'answered')
                    """,
                    (
                        company_id, sdg_no, code, 1,
                        f"{code} için durum değerlendirmesi",
                        "Var", 1.0, "Yıllık"
                    )
                )
                inserted += 1
            except Exception as e:
                logging.info(f"SDG yanıt eklenemedi ({code}): {e}")

    elif {'company_id', 'question_id', 'response_text', 'response_value'}.issubset(cols):
        # sdg_question_bank tablosundan question_id bulup kayıt ekle
        q_cols = set(table_columns(cur, 'sdg_question_bank'))
        if {'indicator_code', 'id'}.issubset(q_cols):
            for code in sample_indicators:
                try:
                    cur.execute("SELECT id FROM sdg_question_bank WHERE indicator_code=? LIMIT 1", (code,))
                    row = cur.fetchone()
                    if not row:
                        continue
                    q_id = row[0]
                    cur.execute(
                        """
                        INSERT INTO sdg_question_responses(
                            company_id, question_id, response_text, response_value, is_validated
                        ) VALUES (?, ?, ?, ?, 1)
                        """,
                        (company_id, q_id, f"{code} için tohum yanıt", "1")
                    )
                    inserted += 1
                except Exception as e:
                    logging.info(f"SDG(questions) yanıt eklenemedi ({code}): {e}")
        else:
            logging.warning("Uyarı: sdg_question_bank bulunamadı; SDG yanıt tohumlama atlandı.")
    else:
        logging.warning("Uyarı: sdg_question_responses beklenen şemaya uymuyor; SDG yanıt tohumlama atlandı.")

    return inserted


def compute_material_type(impact_score: int, financial_score: int) -> Tuple[int, str]:
    is_material = 1 if (impact_score >= 3 or financial_score >= 3) else 0
    if impact_score >= 3 and financial_score >= 3:
        material_type = 'double'
    elif impact_score >= 3:
        material_type = 'impact_only'
    elif financial_score >= 3:
        material_type = 'financial_only'
    else:
        material_type = 'none'
    return is_material, material_type


def seed_tsrs_materiality(conn: sqlite3.Connection, company_id: int, period: str) -> int:
    cur = conn.cursor()
    # Tabloyu güvenceye al (varsa dokunmaz)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tsrs_materiality_assessment (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            indicator_id INTEGER NOT NULL,
            assessment_period TEXT NOT NULL,
            impact_score INTEGER,
            financial_score INTEGER,
            is_material BOOLEAN,
            material_type TEXT,
            stakeholder_input TEXT,
            assessment_rationale TEXT,
            approved_by TEXT,
            approved_at TEXT,
            UNIQUE(company_id, indicator_id, assessment_period)
        )
        """
    )

    # DB'deki ilk 3 TSRS göstergesini al
    cur.execute("SELECT id, code FROM tsrs_indicators ORDER BY code LIMIT 3")
    indicators = cur.fetchall()
    inserted = 0

    for ind_id, code in indicators:
        try:
            impact_score, financial_score = 4, 4
            is_material, material_type = compute_material_type(impact_score, financial_score)
            cur.execute(
                """
                INSERT OR IGNORE INTO tsrs_materiality_assessment(
                    company_id, indicator_id, assessment_period, impact_score, financial_score,
                    is_material, material_type, stakeholder_input, assessment_rationale, approved_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id, ind_id, period,
                    impact_score, financial_score,
                    is_material, material_type,
                    '{"stakeholders":"yüksek öncelik"}',
                    f"{code} için örnek materyalite değerlendirmesi",
                    "Sürdürülebilirlik Müdürü"
                )
            )

            # Varsa mevcut satırı güncelle (INSERT IGNORE yapılmışsa)
            cur.execute(
                """
                UPDATE tsrs_materiality_assessment
                SET impact_score=?, financial_score=?, is_material=?, material_type=?,
                    assessment_rationale=?
                WHERE company_id=? AND indicator_id=? AND assessment_period=?
                """,
                (
                    impact_score, financial_score, is_material, material_type,
                    f"{code} için örnek materyalite değerlendirmesi",
                    company_id, ind_id, period
                )
            )
            inserted += 1
        except Exception as e:
            logging.info(f"TSRS materyalite eklenemedi ({code}): {e}")

    return inserted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--company', type=int, default=1)
    ap.add_argument('--period', default='2025')
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        sdg_count = seed_sdg_question_responses(conn, args.company, args.period)
        tsrs_count = seed_tsrs_materiality(conn, args.company, args.period)
        conn.commit()
        logging.info(f"Tohumlama tamamlandı: SDG yanıtları={sdg_count}, TSRS materyalite={tsrs_count}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
