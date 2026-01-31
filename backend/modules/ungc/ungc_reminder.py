#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Reminder System
Automatic reminders for COP reporting and KPI updates
"""
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class UNGCReminderSystem:
    """Automatic reminder system for UNGC compliance"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_reminder_table()

    def _create_reminder_table(self):
        """Create reminder table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ungc_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                reminder_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_cop_reminder(self, company_id: int, year: int) -> int:
        """
        Create COP report submission reminder
        
        Args:
            company_id: Company ID
            year: Reporting year
            
        Returns:
            Reminder ID
        """
        # COP due date: June 30 of following year
        due_date = datetime(year + 1, 6, 30)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ungc_reminders (company_id, reminder_type, title, description, due_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            'cop_submission',
            f'COP Report Submission - {year}',
            f'Submit your Communication on Progress (COP) report for {year} by June 30, {year+1}',
            due_date.strftime('%Y-%m-%d')
        ))

        reminder_id = int(cursor.lastrowid or 0)
        conn.commit()
        conn.close()

        return reminder_id

    def create_kpi_update_reminder(self, company_id: int, principle_id: str,
                                   due_date: datetime) -> int:
        """
        Create KPI data update reminder
        
        Args:
            company_id: Company ID
            principle_id: Principle ID (e.g., 'P1')
            due_date: Due date
            
        Returns:
            Reminder ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ungc_reminders (company_id, reminder_type, title, description, due_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            'kpi_update',
            f'Update KPI Data - Principle {principle_id}',
            f'Please update KPI data for Principle {principle_id}',
            due_date.strftime('%Y-%m-%d')
        ))

        reminder_id = int(cursor.lastrowid or 0)
        conn.commit()
        conn.close()

        return reminder_id

    def get_pending_reminders(self, company_id: int) -> List[Dict]:
        """
        Get all pending reminders for a company
        
        Args:
            company_id: Company ID
            
        Returns:
            List of pending reminders
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, reminder_type, title, description, due_date, created_at
            FROM ungc_reminders
            WHERE company_id = ? AND status = 'pending'
            ORDER BY due_date ASC
        """, (company_id,))

        reminders = []
        for row in cursor.fetchall():
            due_date = datetime.strptime(row[4], '%Y-%m-%d')
            days_until = (due_date - datetime.now()).days

            reminders.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'description': row[3],
                'due_date': row[4],
                'days_until': days_until,
                'urgency': 'high' if days_until <= 7 else 'medium' if days_until <= 30 else 'low'
            })

        conn.close()
        return reminders

    def mark_reminder_completed(self, reminder_id: int):
        """Mark a reminder as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ungc_reminders
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reminder_id,))

        conn.commit()
        conn.close()

    def auto_create_annual_reminders(self, company_id: int):
        """
        Automatically create annual reminders for a company
        
        Creates:
        - COP submission reminder
        - Quarterly KPI update reminders
        """
        current_year = datetime.now().year

        # COP reminder
        self.create_cop_reminder(company_id, current_year)

        # Quarterly KPI update reminders for all principles
        principles = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']

        # Q1: End of March
        q1_date = datetime(current_year, 3, 31)
        # Q2: End of June
        q2_date = datetime(current_year, 6, 30)
        # Q3: End of September
        q3_date = datetime(current_year, 9, 30)
        # Q4: End of December
        q4_date = datetime(current_year, 12, 31)

        for principle in principles:
            # Only create future reminders
            if q1_date > datetime.now():
                self.create_kpi_update_reminder(company_id, principle, q1_date)
            if q2_date > datetime.now():
                self.create_kpi_update_reminder(company_id, principle, q2_date)
            if q3_date > datetime.now():
                self.create_kpi_update_reminder(company_id, principle, q3_date)
            if q4_date > datetime.now():
                self.create_kpi_update_reminder(company_id, principle, q4_date)


if __name__ == '__main__':
    # Test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH

    reminder = UNGCReminderSystem(db)

    # Create annual reminders
    reminder.auto_create_annual_reminders(company_id=1)

    # Get pending reminders
    pending = reminder.get_pending_reminders(company_id=1)
    logging.info(f"Pending reminders: {len(pending)}")
    for r in pending:
        logging.info(f"  [{r['urgency']}] {r['title']} - Due in {r['days_until']} days")

