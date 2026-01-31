#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
from typing import Optional

from config.settings import ensure_directories, get_db_path
from modules.water_management.water_manager import WaterManager
from modules.water_management.water_reporting import WaterReporting

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def upsert_company(conn: sqlite3.Connection, name: str = "Sustainage") -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sector TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS company_info (
            company_id INTEGER PRIMARY KEY,
            sirket_adi TEXT NOT NULL,
            ticari_unvan TEXT,
            aktif INTEGER DEFAULT 1
        )
        """
    )
    cur.execute(
        "INSERT OR IGNORE INTO company_info(company_id, sirket_adi, ticari_unvan, aktif) VALUES (1, ?, ?, 1)",
        (name, name),
    )
    cur.execute(
        "UPDATE company_info SET sirket_adi=?, ticari_unvan=?, aktif=1 WHERE company_id=1",
        (name, name),
    )
    cur.execute(
        "INSERT OR IGNORE INTO companies(id, name, sector, is_active) VALUES (1, ?, 'Genel', 1)",
        (name,),
    )
    cur.execute(
        "UPDATE companies SET name=?, is_active=1 WHERE id=1",
        (name,),
    )
    conn.commit()


def add_water_samples(manager: WaterManager, company_id: int = 1, period: str = "2024") -> None:
    samples = [
        dict(period=period, consumption_type="industrial", water_source="municipal", blue_water=1200.0, green_water=150.0, grey_water=80.0, efficiency_ratio=0.85, recycling_rate=0.20, location="Tesis A", process_description="Üretim ve soğutma", measurement_method="measurement", data_quality="high"),
        dict(period=period, consumption_type="cooling", water_source="groundwater", blue_water=800.0, green_water=100.0, grey_water=50.0, efficiency_ratio=0.90, recycling_rate=0.30, location="Tesis B", process_description="Soğutma kulesi", measurement_method="calculation", data_quality="medium"),
        dict(period=period, consumption_type="sanitary", water_source="municipal", blue_water=300.0, green_water=0.0, grey_water=120.0, efficiency_ratio=0.70, recycling_rate=0.10, location="Ofis", process_description="Sanitary", measurement_method="measurement", data_quality="medium"),
    ]
    for s in samples:
        manager.add_water_consumption(company_id, **s)


def main() -> Optional[str]:
    ensure_directories()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        upsert_company(conn, "Sustainage")
    finally:
        conn.close()

    wm = WaterManager(db_path)
    add_water_samples(wm, 1, "2024")

    wr = WaterReporting(db_path)
    report_path = wr.generate_water_footprint_report(1, "2024")
    return report_path


if __name__ == "__main__":
    path = main()
    logging.info(f"OK - Water report generated: {path}")
