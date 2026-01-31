#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 1 - Yoksulluğa Son
Veri Giriş Formu
"""

import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import sqlite3
from typing import Dict, List, Optional

from modules.data_collection.form_builder import FormField
from config.database import DB_PATH


def get_sdg1_fields() -> List[FormField]:
    """SDG 1 için form alanları"""
    return [
        FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024',
                 ['2024', '2023', '2022'], help_text='Verilerin ait olduğu yıl'),

        FormField('employees_below_poverty', 'Yoksulluk Sınırının Altında Çalışan Sayısı',
                 'number', False, unit='kişi',
                 help_text='Asgari ücretin altında kazanç sağlayan çalışan sayısı'),

        FormField('living_wage_ratio', 'Yaşanabilir Ücret Oranı', 'number', False, unit='%',
                 help_text='Yaşanabilir ücreti alan çalışan yüzdesi'),

        FormField('social_support_programs', 'Sosyal Destek Programları', 'textarea', False,
                 help_text='Çalışanlara yönelik sosyal destek programları'),

        FormField('community_poverty_projects', 'Toplum Yoksulluk Projeleri', 'textarea', False,
                 help_text='Yerel toplulukta yoksullukla mücadele projeleri'),

        FormField('notes', 'Ek Notlar', 'textarea', False),
    ]

def save_sdg1_data(form_data: Dict, is_draft: bool, company_id: int, task_id: Optional[int] = None) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS sdg1_poverty_data (
            id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT,
            employees_below_poverty REAL, living_wage_ratio REAL, social_support_programs TEXT,
            community_poverty_projects TEXT, notes TEXT, is_draft INTEGER, 
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

        cursor.execute("""INSERT INTO sdg1_poverty_data (company_id, task_id, reporting_year, 
            employees_below_poverty, living_wage_ratio, social_support_programs, community_poverty_projects,
            notes, is_draft) VALUES (?,?,?,?,?,?,?,?,?)""",
            (company_id, task_id, form_data.get('reporting_year'), form_data.get('employees_below_poverty'),
             form_data.get('living_wage_ratio'), form_data.get('social_support_programs'),
             form_data.get('community_poverty_projects'), form_data.get('notes'), 1 if is_draft else 0))

        if task_id and not is_draft:
            cursor.execute("UPDATE tasks SET progress=100, status='Tamamlandı' WHERE id=?", (task_id,))
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"[HATA] SDG 1: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

