
import sys
import os
import sqlite3
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config.database import get_db_path
from backend.modules.gri.gri_manager import GRIManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_duplicates():
    db_path = get_db_path()
    
    # Ensure tables exist
    try:
        GRIManager(db_path=db_path)
    except Exception as e:
        logger.warning(f"Could not initialize GRIManager (tables might not be created): {e}")

    logger.info(f"Cleaning duplicates in {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Find duplicate codes
        cursor.execute("""
            SELECT code, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM gri_indicators
            GROUP BY code
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        
        logger.info(f"Found {len(duplicates)} duplicate codes.")
        
        for row in duplicates:
            code = row['code']
            ids = [int(id) for id in row['ids'].split(',')]
            ids.sort()
            
            keep_id = ids[0] # Keep the first one (oldest)
            remove_ids = ids[1:]
            
            logger.info(f"Processing '{code}': Keeping {keep_id}, removing {remove_ids}")
            
            # 2. Update references
            placeholders = ','.join('?' * len(remove_ids))
            
            # gri_responses
            cursor.execute(f"""
                UPDATE gri_responses 
                SET indicator_id = ? 
                WHERE indicator_id IN ({placeholders})
            """, (keep_id, *remove_ids))
            
            # gri_selections
            cursor.execute(f"""
                UPDATE gri_selections 
                SET indicator_id = ? 
                WHERE indicator_id IN ({placeholders})
            """, (keep_id, *remove_ids))
            
            # 3. Delete duplicates
            cursor.execute(f"""
                DELETE FROM gri_indicators 
                WHERE id IN ({placeholders})
            """, tuple(remove_ids))
            
        conn.commit()
        logger.info("Duplicates removed.")
        
        # 4. Create Unique Index
        logger.info("Creating unique index on gri_indicators(code)...")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_gri_indicators_code ON gri_indicators(code)")
        conn.commit()
        logger.info("Unique index created successfully.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error cleaning duplicates: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_duplicates()
