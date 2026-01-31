
import sqlite3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.database import DB_PATH
from backend.modules.sdg.sdg_data_validation import SDGDataValidation

def fix_validation_rules():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update consistency_check rule
    print("Updating consistency_check rule...")
    cursor.execute("""
        UPDATE sdg_validation_rules 
        SET validation_expression = 'g.code IS NULL OR i.code IS NULL'
        WHERE rule_name = 'consistency_check'
    """)
    
    # 2. Check if there are other rules using aliases
    cursor.execute("SELECT rule_name, validation_expression FROM sdg_validation_rules")
    rules = cursor.fetchall()
    print("Current rules:")
    for name, expr in rules:
        print(f"  - {name}: {expr}")
        
    # 3. Check data in sdg_question_responses
    cursor.execute("SELECT COUNT(*) FROM sdg_question_responses WHERE company_id = 1")
    count = cursor.fetchone()[0]
    print(f"Total responses for company 1: {count}")
    
    if count == 0:
        print("No responses found. Creating dummy data for testing...")
        # Create some dummy responses
        # Get some question IDs
        cursor.execute("SELECT id FROM sdg_question_bank LIMIT 5")
        q_ids = [row[0] for row in cursor.fetchall()]
        
        for q_id in q_ids:
            # Insert valid response
            cursor.execute("""
                INSERT INTO sdg_question_responses (company_id, question_id, response_value, response_date)
                VALUES (1, ?, 'Test response', date('now'))
            """, (q_id,))
            
        # Insert some invalid responses to trigger rules
        # Missing data
        cursor.execute("""
            INSERT INTO sdg_question_responses (company_id, question_id, response_value, response_date)
            VALUES (1, ?, '', date('now'))
        """, (q_ids[0],))
        
        print("Dummy data created.")
        
    conn.commit()
    conn.close()
    
    # 4. Run validation
    print("Running validation...")
    validator = SDGDataValidation()
    results = validator.validate_company_data(1)
    print("Validation results:")
    print(f"  Failed rules: {results.get('failed_rules')}")
    print(f"  Quality scores: {results.get('quality_scores')}")
    
    # Check if results are saved in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sdg_validation_results WHERE company_id = 1")
    res_count = cursor.fetchone()[0]
    print(f"Validation results in DB: {res_count}")
    conn.close()

if __name__ == "__main__":
    fix_validation_rules()
