import sys
import os
import logging
from datetime import datetime

# Setup paths
# tools/verify...py -> tools -> sustainage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

# Correct imports using full path
from backend.modules.automated_reporting.auto_report import AutoReportManager
from backend.modules.analytics.trend_analyzer import TrendAnalyzer
from backend.config.database import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify_data():
    company_id = 1 # Test company
    
    print(f"--- Verifying Data for Company {company_id} ---")
    
    # 1. Verify Automated Reporting
    try:
        print("\n[Automated Reporting]")
        report_mgr = AutoReportManager(DB_PATH)
        reports = report_mgr.get_scheduled_reports(company_id)
        print(f"Found {len(reports)} scheduled reports.")
        for r in reports:
            # sqlite3.Row might behave differently in some envs, let's be safe
            report_type = r['report_type'] if hasattr(r, '__getitem__') else getattr(r, 'report_type', 'N/A')
            frequency = r['frequency'] if hasattr(r, '__getitem__') else getattr(r, 'frequency', 'N/A')
            email_to = r['email_to'] if hasattr(r, '__getitem__') else getattr(r, 'email_to', 'N/A')
            
            print(f" - {report_type} ({frequency}) to {email_to}")
            
        if len(reports) > 0:
            print("PASS: Automated Reporting data found.")
        else:
            print("FAIL: No scheduled reports found (did dummy data script run?).")
            
    except Exception as e:
        print(f"ERROR in Automated Reporting: {e}")

    # 2. Verify Analytics (Trend)
    try:
        print("\n[Analytics]")
        trend_mgr = TrendAnalyzer(DB_PATH)
        years = [2020, 2021, 2022, 2023, 2024, 2025]
        
        # Check Carbon Emissions Trend (populated by dummy data)
        # Dummy data script added emissions for 'Company Fleet 2023' etc.
        # But wait, dummy data script used `carbon_calc.save_emission`.
        # Let's see if save_emission populates 'carbon_emissions' table with 'amount' column.
        
        # NOTE: Carbon Emissions table uses period_start, not year column.
        trends = trend_mgr.get_metric_trend(company_id, 'carbon_emissions', 'amount', years, date_column='period_start')
        print(f"Found {len(trends)} data points for Carbon Emissions.")
        for t in trends:
            print(f" - Year {t['year']}: {t['value']}")
            
        if len(trends) > 0:
            print("PASS: Analytics trend data found.")
            stats = trend_mgr.calculate_trend_statistics(trends)
            print(f"Stats: {stats}")
        else:
            print("FAIL: No trend data found.")
            
    except Exception as e:
        print(f"ERROR in Analytics: {e}")

if __name__ == "__main__":
    verify_data()
