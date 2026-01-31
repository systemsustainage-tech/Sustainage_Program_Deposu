import sys
import os
import json
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def test_full_stakeholder_flow():
    print("Testing Stakeholder Engagement Full Flow...")
    
    # Initialize
    engagement = StakeholderEngagement(DB_PATH)
    
    # 1. Test Employee Survey Creation
    print("\n[1] Creating Employee Survey...")
    link_emp = engagement.create_employee_satisfaction_survey(1, duration_days=15)
    if link_emp:
        print(f"PASS: Employee Survey Created: {link_emp}")
    else:
        print("FAIL: Could not create employee survey")

    # 2. Test Stakeholder Survey Creation
    print("\n[2] Creating Stakeholder Survey...")
    link_sh = engagement.create_stakeholder_satisfaction_survey(1, duration_days=45)
    if link_sh:
        print(f"PASS: Stakeholder Survey Created: {link_sh}")
    else:
        print("FAIL: Could not create stakeholder survey")
        
    # 3. Verify Survey Type in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT survey_type, survey_link FROM online_surveys ORDER BY id DESC LIMIT 2")
    rows = cursor.fetchall()
    print(f"\n[3] DB Verification (Latest 2 surveys): {rows}")
    conn.close()
    
    # 4. Test Training Material
    print("\n[4] Adding Training Material...")
    mat_id = engagement.add_training_material(1, "Sustainability 101", "http://video.url", "Intro course")
    if mat_id:
        print(f"PASS: Material Added ID: {mat_id}")
    else:
        print("FAIL: Could not add material")
        
    # 5. Assign and Update Training
    # Get a stakeholder ID (create one if needed)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM stakeholders LIMIT 1")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO stakeholders (company_id, stakeholder_type, stakeholder_name) VALUES (1, 'calisan', 'Test User')")
        sid = cursor.lastrowid
    else:
        sid = row[0]
    conn.commit()
    conn.close()
    
    print(f"\n[5] Assigning Training to Stakeholder {sid}...")
    if engagement.assign_training(mat_id, sid):
        print("PASS: Training assigned")
    else:
        print("FAIL: Training assignment failed")
        
    print("\n[6] Updating Training Progress...")
    if engagement.update_training_status(sid, mat_id, 'in_progress', 50):
        print("PASS: Progress updated to 50%")
    else:
        print("FAIL: Progress update failed")

    # 7. Check Progress
    trainings = engagement.get_stakeholder_trainings(sid)
    found = False
    for t in trainings:
        if t['material_id'] == mat_id:
            print(f"PASS: Found training in list: {t['title']} - {t['progress_percentage']}%")
            found = True
            break
    if not found:
        print("FAIL: Training not found in list")

if __name__ == "__main__":
    test_full_stakeholder_flow()
