
import sys
import os
import logging

# Add project root to path
sys.path.append('c:\\SUSTAINAGESERVER')
sys.path.append('/var/www/sustainage')

from config.database import DB_PATH
from backend.modules.environmental.biodiversity_manager import BiodiversityManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    print(f"Migrating Biodiversity Module tables to {DB_PATH}...")
    
    # Ensure DB directory exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        print(f"Creating directory {db_dir}...")
        os.makedirs(db_dir, exist_ok=True)
        
    # Initialize manager which creates tables
    try:
        manager = BiodiversityManager(DB_PATH)
        print("Biodiversity tables created/verified successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
