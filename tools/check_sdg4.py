import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.reporting_journey_manager import ReportingJourneyManager
from config.database import DB_PATH

def check_sdg_step_4():
    print(f"Checking SDG Step 4 Status...")
    print(f"DB Path: {DB_PATH}")
    
    # Check user_sdg_selections table
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM user_sdg_selections")
        count = cursor.fetchone()[0]
        print(f"Total records in user_sdg_selections: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM user_sdg_selections LIMIT 5")
            rows = cursor.fetchall()
            print("Sample selections:")
            for row in rows:
                print(row)
        else:
            print("No selections found in user_sdg_selections table.")
            
    except Exception as e:
        print(f"Error checking table: {e}")
    finally:
        conn.close()

    # Check Reporting Journey Status
    try:
        manager = ReportingJourneyManager(DB_PATH)
        # Assuming company_id = 1 for test
        company_id = 1
        status = manager.get_journey_status(company_id)
        
        step_4 = next((s for s in status if s['number'] == 4), None)
        if step_4:
            print(f"\nStep 4 Status in Journey Manager:")
            print(f"Title: {step_4['title']}")
            print(f"Status: {step_4['status']}")
            print(f"Action Text: {step_4['action_text']}")
        else:
            print("\nStep 4 not found in journey status.")
            
    except Exception as e:
        print(f"Error checking journey manager: {e}")

if __name__ == "__main__":
    check_sdg_step_4()
