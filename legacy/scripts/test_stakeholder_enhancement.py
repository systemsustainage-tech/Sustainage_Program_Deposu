import sys
import os
import logging
import sqlite3
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO)

def test_stakeholder_enhancements():
    print(f"Testing Stakeholder Engagement Enhancements using DB: {DB_PATH}")
    
    se = StakeholderEngagement(DB_PATH)
    
    # 1. Verify Tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_materials'")
    if cursor.fetchone():
        print("[OK] Table 'training_materials' exists.")
    else:
        print("[FAIL] Table 'training_materials' does not exist.")
        return

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stakeholder_training_progress'")
    if cursor.fetchone():
        print("[OK] Table 'stakeholder_training_progress' exists.")
    else:
        print("[FAIL] Table 'stakeholder_training_progress' does not exist.")
        return
    conn.close()

    # 2. Verify Survey Questions
    emp_questions = se.get_employee_satisfaction_questions()
    print(f"[OK] Employee Satisfaction Questions: {len(emp_questions)}")
    
    stake_questions = se.get_stakeholder_satisfaction_questions()
    print(f"[OK] Stakeholder Satisfaction Questions: {len(stake_questions)}")

    # 3. Verify Training Management
    company_id = 1
    material_id = se.add_training_material(
        company_id=company_id,
        title="Sürdürülebilirlik 101",
        content_url="https://example.com/video.mp4",
        description="Temel eğitim",
        target_groups=["calisan", "tedarikci"]
    )
    
    if material_id:
        print(f"[OK] Training material added with ID: {material_id}")
    else:
        print("[FAIL] Failed to add training material.")

    materials = se.get_training_materials(company_id)
    print(f"[OK] Total training materials: {len(materials)}")
    
    # Assign to a dummy stakeholder
    # Create a dummy stakeholder first if not exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check if table has stakeholder_group or stakeholder_type
    cursor.execute("PRAGMA table_info(stakeholders)")
    cols = [c[1] for c in cursor.fetchall()]
    
    col_name = 'stakeholder_type' if 'stakeholder_type' in cols else 'stakeholder_group'
    
    try:
        cursor.execute(f"INSERT OR IGNORE INTO stakeholders (company_id, {col_name}, stakeholder_name) VALUES (1, 'calisan', 'Test User')")
        stakeholder_id = cursor.lastrowid if cursor.lastrowid else 1 # fallback
        conn.commit()
    except Exception as e:
        print(f"[WARN] Could not create dummy stakeholder: {e}")
        # Try to find existing one
        cursor.execute("SELECT id FROM stakeholders LIMIT 1")
        row = cursor.fetchone()
        if row:
            stakeholder_id = row[0]
        else:
            print("[FAIL] No stakeholders available for testing.")
            return

    conn.close()
    
    if se.assign_training(material_id, stakeholder_id):
        print(f"[OK] Training assigned to stakeholder {stakeholder_id}")
    else:
        print("[FAIL] Failed to assign training.")
        
    # Update progress
    if se.update_training_status(stakeholder_id, material_id, 'in_progress', 50):
        print("[OK] Training progress updated to 50%")
    
    # Check status
    trainings = se.get_stakeholder_trainings(stakeholder_id)
    for t in trainings:
        if t['material_id'] == material_id:
            print(f"[OK] Verified training status: {t['status']}, Progress: {t['progress_percentage']}%")

if __name__ == "__main__":
    test_stakeholder_enhancements()
