
import os
import sys
import sqlite3
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.modules.prioritization.prioritization_manager import PrioritizationManager

logging.basicConfig(level=logging.INFO)

def test_double_materiality():
    db_path = os.path.join(os.getcwd(), 'test_materiality.sqlite')
    if os.path.exists(db_path):
        os.remove(db_path)
        
    logging.info(f"Testing with DB: {db_path}")
    
    manager = PrioritizationManager(db_path)
    
    # 1. Check Schema
    conn = manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(materiality_topics)")
    columns = [info[1] for info in cursor.fetchall()]
    logging.info(f"Columns: {columns}")
    
    if 'stakeholder_impact' not in columns or 'business_impact' not in columns:
        logging.error("FAILED: Missing columns stakeholder_impact or business_impact")
        return
    else:
        logging.info("PASSED: Schema check")
        
    # 2. Check Default Topics Population
    # We need a company first? Manager creates tables but doesn't create company.
    # But populate_default_topics uses company_id=1.
    # Foreign key constraint might fail if company 1 doesn't exist?
    # Schema says: FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
    # If companies table is empty, insert will fail.
    # Let's create a company first.
    
    cursor.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO companies (id, name) VALUES (1, 'Test Company')")
    conn.commit()
    
    # Now call populate manually since __init__ might have run before company creation if tables existed?
    # Actually __init__ calls create_tables which calls populate_default_topics.
    # But populate_default_topics runs inside create_tables. 
    # If companies table didn't exist when create_tables ran (it creates materiality_topics which references companies),
    # creating materiality_topics might succeed (sqlite is loose with FKs by default unless enabled).
    # But populate_default_topics insert might fail if FK enforced.
    # Let's run populate explicitly.
    manager.populate_default_topics()
    
    topics = manager.get_materiality_topics(1)
    logging.info(f"Default topics count: {len(topics)}")
    if len(topics) > 0:
        logging.info("PASSED: Default topics population")
    else:
        logging.warning("WARNING: Default topics not populated (might be FK issue in test env)")

    # 3. Add New Topic
    topic_id = manager.save_materiality_topic(
        company_id=1,
        topic_name="Test Double Materiality",
        category="Governance",
        stakeholder_impact=4.5,
        business_impact=3.2,
        priority_score=3.85,
        description="Testing separate scores"
    )
    
    if topic_id:
        logging.info(f"PASSED: Added topic with ID {topic_id}")
    else:
        logging.error("FAILED: Could not add topic")
        return

    # 4. Verify Data
    cursor.execute("SELECT * FROM materiality_topics WHERE id=?", (topic_id,))
    row = cursor.fetchone()
    # row is tuple, need to find indices or use row_factory
    # Columns order: id, company_id, topic_name, category, description, sdg_mapping, priority_score, stakeholder_impact, business_impact, ...
    # Let's use dict factory for verification
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materiality_topics WHERE id=?", (topic_id,))
    row = cursor.fetchone()
    
    if row['stakeholder_impact'] == 4.5 and row['business_impact'] == 3.2:
        logging.info("PASSED: Data verification (Values match)")
    else:
        logging.error(f"FAILED: Data mismatch. Got S:{row['stakeholder_impact']}, B:{row['business_impact']}")

    conn.close()
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    logging.info("Test Complete")

if __name__ == "__main__":
    test_double_materiality()
