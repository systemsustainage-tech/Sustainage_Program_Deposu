import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite"

def test_template_isolation():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Clean up test data (if any)
        cursor.execute("DELETE FROM survey_templates WHERE name LIKE 'TEST_TMPL_%'")
        conn.commit()

        # 2. Insert Test Templates
        # Standard Template (company_id = NULL)
        cursor.execute("INSERT INTO survey_templates (name, company_id) VALUES ('TEST_TMPL_STANDARD', NULL)")
        std_id = cursor.lastrowid
        
        # Company 2 Template
        cursor.execute("INSERT INTO survey_templates (name, company_id) VALUES ('TEST_TMPL_COMP2', 2)")
        c2_id = cursor.lastrowid
        
        # Company 3 Template
        cursor.execute("INSERT INTO survey_templates (name, company_id) VALUES ('TEST_TMPL_COMP3', 3)")
        c3_id = cursor.lastrowid

        conn.commit()
        logging.info(f"Inserted templates: Standard={std_id}, Comp2={c2_id}, Comp3={c3_id}")

        # 3. Define Fetch Function (simulating prioritization_manager logic)
        def get_templates_for_company(company_id):
            sql = "SELECT id, name, company_id FROM survey_templates WHERE (company_id = ? OR company_id IS NULL) AND name LIKE 'TEST_TMPL_%'"
            cursor.execute(sql, (company_id,))
            return cursor.fetchall()

        # 4. Test for Company 2
        tmpl_c2 = get_templates_for_company(2)
        names_c2 = [r[1] for r in tmpl_c2]
        logging.info(f"Company 2 sees: {names_c2}")
        
        if 'TEST_TMPL_STANDARD' in names_c2 and 'TEST_TMPL_COMP2' in names_c2 and 'TEST_TMPL_COMP3' not in names_c2:
            logging.info("PASS: Company 2 isolation correct.")
        else:
            logging.error(f"FAIL: Company 2 isolation incorrect. Expected Standard+Comp2, got {names_c2}")

        # 5. Test for Company 3
        tmpl_c3 = get_templates_for_company(3)
        names_c3 = [r[1] for r in tmpl_c3]
        logging.info(f"Company 3 sees: {names_c3}")
        
        if 'TEST_TMPL_STANDARD' in names_c3 and 'TEST_TMPL_COMP3' in names_c3 and 'TEST_TMPL_COMP2' not in names_c3:
            logging.info("PASS: Company 3 isolation correct.")
        else:
            logging.error(f"FAIL: Company 3 isolation incorrect. Expected Standard+Comp3, got {names_c3}")

        # 6. Test for Company 99 (No specific templates)
        tmpl_c99 = get_templates_for_company(99)
        names_c99 = [r[1] for r in tmpl_c99]
        logging.info(f"Company 99 sees: {names_c99}")
        
        if 'TEST_TMPL_STANDARD' in names_c99 and len(names_c99) == 1:
            logging.info("PASS: Company 99 isolation correct (Standard only).")
        else:
            logging.error(f"FAIL: Company 99 isolation incorrect. Expected Standard only, got {names_c99}")

    except Exception as e:
        logging.error(f"Test failed with error: {e}")
    finally:
        # Cleanup
        cursor.execute("DELETE FROM survey_templates WHERE name LIKE 'TEST_TMPL_%'")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_template_isolation()
