import sys
import os
import sqlite3
import logging

# Add backend path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

# Ensure DB_PATH matches web_app.py
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO)

def test_economic_manager():
    logging.info("Testing EconomicManager...")
    try:
        from modules.economic.economic_manager import EconomicManager
        mgr = EconomicManager(DB_PATH)
        # Add project
        pid = mgr.add_investment_project(1, "Test Project", 100000, "2024-01-01", "Test Desc")
        if not pid:
            logging.error("Failed to add project")
            return False
        
        # Add flows
        mgr.add_project_cash_flow(pid, 1, 20000)
        mgr.add_project_cash_flow(pid, 2, 30000)
        mgr.add_project_cash_flow(pid, 3, 40000)
        mgr.add_project_cash_flow(pid, 4, 50000)
        
        # Check metrics
        projects = mgr.get_investment_projects(1)
        if not projects:
             logging.error("No projects found")
             return False
             
        p = [x for x in projects if x['id'] == pid][0]
        logging.info(f"Project Metrics: ROI={p.get('roi')}, NPV={p.get('npv')}, Payback={p.get('payback_period')}")
        
        if p.get('roi') is None:
            logging.error("Metrics not calculated")
            return False
            
        logging.info("EconomicManager Test PASSED")
        return True
    except Exception as e:
        logging.error(f"EconomicManager Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_benchmark_manager():
    logging.info("Testing BenchmarkManager...")
    try:
        from modules.analytics.sector_benchmark_database import SectorBenchmarkDatabase
        mgr = SectorBenchmarkDatabase(DB_PATH)
        data = mgr.get_all_metrics_for_sector('imalat')
        if not data:
            logging.error("No data returned for 'imalat'")
            return False
            
        logging.info(f"Got {len(data)} metrics for imalat")
        if 'karbon_yogunlugu' not in data:
            logging.error("Missing expected metric")
            return False
            
        logging.info("BenchmarkManager Test PASSED")
        return True
    except Exception as e:
        logging.error(f"BenchmarkManager Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_economic_manager() and test_benchmark_manager():
        logging.info("ALL TESTS PASSED")
    else:
        logging.error("SOME TESTS FAILED")
        sys.exit(1)
