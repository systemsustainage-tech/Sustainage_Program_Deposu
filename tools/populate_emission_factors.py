#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emisyon Faktörleri Kütüphanesini Veritabanına Yükleme Aracı
DEFRA/IPCC verilerini emission_factors tablosuna ekler.
"""

import sys
import os
import logging

# Add project root and backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.modules.environmental.carbon_manager import CarbonManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting emission factors population...")
    
    try:
        # Initialize CarbonManager which triggers _init_db_tables -> import_defra_ipcc_factors
        cm = CarbonManager()
        
        # Verify count
        conn = cm._get_connection() if hasattr(cm, '_get_connection') else None
        if not conn:
            import sqlite3
            conn = sqlite3.connect(cm.db_path)
            
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emission_factors")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emission_factors WHERE source_reference LIKE '%DEFRA%' OR source_reference LIKE '%IPCC%'")
        defra_count = cursor.fetchone()[0]
        
        logger.info(f"Total emission factors: {count}")
        logger.info(f"DEFRA/IPCC factors: {defra_count}")
        
        conn.close()
        logger.info("Population complete.")
        
    except Exception as e:
        logger.error(f"Error populating emission factors: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
