import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

def populate_data_quality():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        logging.info("Populating sdg_data_quality_scores...")
        
        # Check if company 1 exists
        cursor.execute("SELECT id FROM companies WHERE id=1")
        if not cursor.fetchone():
            logging.info("Company 1 not found. Creating it...")
            cursor.execute("INSERT INTO companies (id, name) VALUES (1, 'Demo Company')")

        # Insert sample quality score for company 1
        # Insert a general score (sdg_no=NULL) and some specific scores
        
        quality_data = [
            # General score
            (1, None, None, 85.0, 90.0, 95.0, 80.0, 87.5, datetime.now().isoformat()),
            # SDG 1 score
            (1, 1, None, 70.0, 80.0, 90.0, 75.0, 78.75, datetime.now().isoformat()),
            # SDG 13 score
            (1, 13, None, 90.0, 95.0, 100.0, 90.0, 93.75, datetime.now().isoformat())
        ]

        cursor.executemany("""
            INSERT INTO sdg_data_quality_scores 
            (company_id, sdg_no, indicator_code, completeness_score, accuracy_score, 
             consistency_score, timeliness_score, overall_quality_score, validation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, quality_data)
        
        logging.info(f"Inserted {len(quality_data)} rows into sdg_data_quality_scores")
        
        conn.commit()
        logging.info("Data quality scores populated successfully.")

    except Exception as e:
        logging.error(f"Error populating data quality scores: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_data_quality()
