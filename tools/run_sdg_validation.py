#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run SDG Validation - Populates sdg_validation_results table
"""

import sys
import os
import logging

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.modules.sdg.sdg_data_validation import SDGDataValidation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        logging.info("Starting SDG Data Validation...")
        
        # Initialize validator
        validator = SDGDataValidation()
        
        # Run validation for company ID 1 (default/test company)
        company_id = 1
        logging.info(f"Validating data for Company ID: {company_id}")
        
        results = validator.validate_company_data(company_id)
        
        if 'error' in results:
            logging.error(f"Validation failed: {results['error']}")
        else:
            logging.info("Validation completed successfully.")
            logging.info(f"Quality Scores: {results.get('quality_scores', {})}")
            
            # Check if data was inserted
            import sqlite3
            from config.database import DB_PATH
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sdg_validation_results WHERE company_id = ?", (company_id,))
            count = cursor.fetchone()[0]
            logging.info(f"Total validation results in DB for company {company_id}: {count}")
            conn.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
