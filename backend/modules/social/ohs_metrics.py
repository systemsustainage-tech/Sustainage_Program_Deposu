#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İş Sağlığı ve Güvenliği (İSG) Modülü
Kaza, hastalık, eğitim ve İSG metrikleri
GRI 403
"""

import logging
import os
import sqlite3
from typing import Dict


class OHSMetrics:
    """İş Sağlığı ve Güvenliği metrikleri"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """İSG tabloları"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ohs_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    incident_date TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT,
                    days_lost INTEGER DEFAULT 0,
                    fatality INTEGER DEFAULT 0,
                    gender TEXT,
                    department TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ohs_training (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    training_type TEXT NOT NULL,
                    participants INTEGER DEFAULT 0,
                    hours REAL DEFAULT 0,
                    cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] ISG tablolari hazir")
        except Exception as e:
            logging.error(f"[HATA] ISG tablo: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_incident(self, company_id: int, incident_date: str, incident_type: str,
                    severity: str = 'Hafif', days_lost: int = 0, fatality: bool = False, **kwargs) -> int:
        """Kaza/olay kaydı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ohs_incidents 
                (company_id, incident_date, incident_type, severity, days_lost, fatality,
                 gender, department, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, incident_date, incident_type, severity, days_lost,
                  1 if fatality else 0, kwargs.get('gender'), kwargs.get('department'),
                  kwargs.get('description')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_training(self, company_id: int, year: int, training_type: str,
                    participants: int, hours: float, **kwargs) -> int:
        """İSG eğitimi kaydı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ohs_training 
                (company_id, period_year, training_type, participants, hours, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, year, training_type, participants, hours, kwargs.get('cost')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_summary(self, company_id: int, year: int) -> Dict:
        """Yıllık İSG özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Kaza istatistikleri
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_incidents,
                    SUM(days_lost) as total_days_lost,
                    SUM(fatality) as total_fatalities,
                    SUM(CASE WHEN severity='Ağır' THEN 1 ELSE 0 END) as serious_incidents
                FROM ohs_incidents
                WHERE company_id=? AND strftime('%Y', incident_date)=?
            """, (company_id, str(year)))
            row = cursor.fetchone()

            # Eğitim istatistikleri
            cursor.execute("""
                SELECT SUM(participants), SUM(hours)
                FROM ohs_training
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            training = cursor.fetchone()

            # İş gücü sayısı (İK'dan)
            cursor.execute("""
                SELECT SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            workforce = cursor.fetchone()[0] or 1

            # LTIFR (Lost Time Injury Frequency Rate) - 200,000 saat başına
            hours_worked = workforce * 2000  # Yıllık ortalama çalışma saati
            incidents = row[0] or 0
            ltifr = (incidents / hours_worked * 200000) if hours_worked > 0 else 0

            return {
                'total_incidents': int(incidents),
                'days_lost': int(row[1] or 0),
                'fatalities': int(row[2] or 0),
                'serious_incidents': int(row[3] or 0),
                'ltifr': round(ltifr, 2),
                'training_participants': int(training[0] or 0),
                'training_hours': round(training[1] or 0, 2),
                'year': year
            }
        finally:
            conn.close()

