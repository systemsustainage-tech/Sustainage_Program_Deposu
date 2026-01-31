
import sys
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add project root and backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from config.database import DB_PATH
from backend.modules.csrd.csrd_compliance_manager import CSRDComplianceManager
from backend.modules.iirc.iirc_manager import IIRCManager

def test_csrd_saving():
    print("\n--- Testing CSRD Data Saving ---")
    manager = CSRDComplianceManager(DB_PATH)
    
    # Ensure tables exist
    manager._init_csrd_tables()
    
    company_id = 1
    topic_code = "TEST-E1"
    topic_name = "Test Climate Change"
    impact = 5
    financial = 4
    rationale = "Test rationale"
    
    print(f"Attempting to add materiality assessment for Company {company_id}...")
    result = manager.add_materiality_assessment(
        company_id, topic_code, topic_name, impact, financial, rationale
    )
    
    if result:
        print("SUCCESS: add_materiality_assessment returned result.")
    else:
        print("FAILURE: add_materiality_assessment returned empty/None.")
        return

    # Verify in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM double_materiality_assessment 
        WHERE company_id = ? AND topic_code = ?
        ORDER BY id DESC LIMIT 1
    """, (company_id, topic_code))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"SUCCESS: Found record in DB: {row}")
    else:
        print("FAILURE: Record NOT found in DB after saving.")

def test_iirc_saving():
    print("\n--- Testing IIRC Data Saving ---")
    manager = IIRCManager(DB_PATH)
    
    company_id = 1
    year = 2025
    report_name = "Test Integrated Report"
    description = "Test Description"
    capitals = {
        'financial': "Financial Capital Data",
        'human': "Human Capital Data"
    }
    
    print(f"Attempting to add IIRC report for Company {company_id}...")
    
    result = manager.add_report(company_id, year, report_name, description, capitals)
    
    if result:
        print("SUCCESS: add_report returned True.")
    else:
        print("FAILURE: add_report returned False.")
        return

    # Verify in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM integrated_reports 
        WHERE company_id = ? AND year = ?
        ORDER BY id DESC LIMIT 1
    """, (company_id, year))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"SUCCESS: Found record in DB: {row}")
    else:
        print("FAILURE: Record NOT found in DB after saving.")

if __name__ == "__main__":
    print(f"Using DB_PATH: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("WARNING: DB file does not exist!")
    
    test_csrd_saving()
    test_iirc_saving()
