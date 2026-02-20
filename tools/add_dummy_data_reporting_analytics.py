import sys
import os
import sqlite3
import logging
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config.database import DB_PATH
from backend.modules.automated_reporting.auto_report import AutoReportManager
# Note: importing AutoReportManager might fail if filename is auto_report.py and we import from auto_report
# Correct import:
from backend.modules.automated_reporting.auto_report import AutoReportManager
from backend.modules.environmental.carbon_calculator import CarbonCalculator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # carbon_emissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_emissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            scope INTEGER,
            category TEXT,
            subcategory TEXT,
            amount REAL,
            unit TEXT,
            emission_factor REAL,
            co2e_kg REAL,
            period_start TEXT,
            period_end TEXT,
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # scheduled_reports table (AutoReportManager creates it, but good to ensure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            report_type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            email_to TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Tables created/verified.")

def add_dummy_data():
    company_id = 1
    
    # 1. Scheduled Reports
    try:
        report_mgr = AutoReportManager(DB_PATH, company_id=company_id)
        existing = report_mgr.get_scheduled_reports(company_id)
        if not existing:
            logger.info("Adding dummy scheduled reports...")
            report_mgr.schedule_report(company_id, "monthly_summary", "monthly", "info@sustainage.app")
            report_mgr.schedule_report(company_id, "carbon_alert", "weekly", "admin@sustainage.app")
        else:
            logger.info("Scheduled reports already exist.")
            
    except Exception as e:
        logger.error(f"Error adding scheduled reports: {e}")

    # 2. Carbon Emissions (for Trend Analysis)
    try:
        carbon_calc = CarbonCalculator(DB_PATH, company_id=company_id)
        
        # Check if we have data for 2023, 2024, 2025
        # We can check by querying or just add if we suspect it's empty.
        # Simple check:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM carbon_emissions WHERE company_id = ?", (company_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        if count < 5:
            logger.info("Adding dummy carbon emissions...")
            
            # 2023 Data
            calc1 = carbon_calc.calculate_scope1_fuel('diesel', 5000, 'litre')
            carbon_calc.save_emission(company_id, calc1, '2023-01-01', '2023-12-31', 'Company Fleet 2023')
            
            calc2 = carbon_calc.calculate_scope2_electricity(120000)
            carbon_calc.save_emission(company_id, calc2, '2023-01-01', '2023-12-31', 'Electricity 2023')
            
            # 2024 Data (Increased)
            calc3 = carbon_calc.calculate_scope1_fuel('diesel', 5500, 'litre')
            carbon_calc.save_emission(company_id, calc3, '2024-01-01', '2024-12-31', 'Company Fleet 2024')
            
            calc4 = carbon_calc.calculate_scope2_electricity(115000) # Efficiency improvement
            carbon_calc.save_emission(company_id, calc4, '2024-01-01', '2024-12-31', 'Electricity 2024')
            
            # 2025 Data (Projected/Current)
            calc5 = carbon_calc.calculate_scope1_fuel('diesel', 6000, 'litre')
            carbon_calc.save_emission(company_id, calc5, '2025-01-01', '2025-12-31', 'Company Fleet 2025')
            
            calc6 = carbon_calc.calculate_scope2_electricity(110000)
            carbon_calc.save_emission(company_id, calc6, '2025-01-01', '2025-12-31', 'Electricity 2025')
            
            logger.info("Carbon emissions added.")
        else:
            logger.info("Carbon emissions already exist.")
            
    except Exception as e:
        logger.error(f"Error adding carbon emissions: {e}")

if __name__ == "__main__":
    create_tables(DB_PATH)
    add_dummy_data()
