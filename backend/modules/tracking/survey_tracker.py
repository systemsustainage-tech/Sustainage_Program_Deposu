#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anket Takip Sistemi
Anket tamamlanma, gecikme ve veri kalitesi takibi
"""

import os
import sqlite3
from typing import Dict, List


class SurveyTracker:
    """Anket izleme ve takip"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

    def get_completion_dashboard(self, company_id: int) -> Dict:
        """Anket tamamlanma dashboard'u"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Toplam anket ataması
            cursor.execute("""
                SELECT COUNT(*) FROM survey_assignments sa
                JOIN surveys s ON sa.survey_id = s.id
                WHERE s.category IN ('SDG', 'GRI', 'TSRS')
            """)
            total = cursor.fetchone()[0]

            # Tamamlanan
            cursor.execute("""
                SELECT COUNT(*) FROM survey_assignments
                WHERE status = 'Tamamlandi'
            """)
            completed = cursor.fetchone()[0]

            # Bekleyen
            cursor.execute("""
                SELECT COUNT(*) FROM survey_assignments
                WHERE status = 'Bekliyor'
            """)
            pending = cursor.fetchone()[0]

            # Geciken
            cursor.execute("""
                SELECT COUNT(*) FROM survey_assignments
                WHERE status != 'Tamamlandi' AND due_date < date('now')
            """)
            overdue = cursor.fetchone()[0]

            return {
                'total': total,
                'completed': completed,
                'pending': pending,
                'overdue': overdue,
                'completion_rate': round((completed/total*100) if total > 0 else 0, 2)
            }

        finally:
            conn.close()

    def get_category_status(self, company_id: int) -> Dict:
        """Kategori bazında durum (SDG, GRI, TSRS)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT s.category, sa.status, COUNT(*)
                FROM survey_assignments sa
                JOIN surveys s ON sa.survey_id = s.id
                GROUP BY s.category, sa.status
            """)

            results = {}
            for row in cursor.fetchall():
                category = row[0]
                status = row[1]
                count = row[2]

                if category not in results:
                    results[category] = {}
                results[category][status] = count

            return results

        finally:
            conn.close()

    def get_department_progress(self, company_id: int) -> List[Dict]:
        """Departman bazında ilerleme"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT u.department, sa.status, COUNT(*)
                FROM survey_assignments sa
                JOIN users u ON sa.assigned_to = u.id
                GROUP BY u.department, sa.status
            """)

            dept_data = {}
            for row in cursor.fetchall():
                dept = row[0] or 'Bilinmeyen'
                status = row[1]
                count = row[2]

                if dept not in dept_data:
                    dept_data[dept] = {'total': 0, 'completed': 0}

                dept_data[dept]['total'] += count
                if status == 'Tamamlandi':
                    dept_data[dept]['completed'] += count

            # Liste formatına çevir
            result = []
            for dept, data in dept_data.items():
                rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
                result.append({
                    'department': dept,
                    'total': data['total'],
                    'completed': data['completed'],
                    'rate': round(rate, 2)
                })

            result.sort(key=lambda x: x['rate'], reverse=True)
            return result

        finally:
            conn.close()

