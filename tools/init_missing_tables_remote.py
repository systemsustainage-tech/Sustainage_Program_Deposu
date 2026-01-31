import os
import sys
import logging

# Add project root and backend to path
# sys.path.append('/var/www/sustainage')  # Conflicts with backend/config
sys.path.append('/var/www/sustainage/backend')

# Import directly from modules if possible, to match how web_app works
try:
    from modules.tsrs.tsrs_manager import TSRSManager
except ImportError:
    from backend.modules.tsrs.tsrs_manager import TSRSManager

try:
    from modules.gri.gri_schema_upgrade import GRISchemaUpgrade
except ImportError:
    from backend.modules.gri.gri_schema_upgrade import GRISchemaUpgrade


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_tables():
    print("Starting table initialization...")
    
    # Initialize TSRS Tables
    try:
        print("Initializing TSRS tables...")
        tsrs_manager = TSRSManager()
        if tsrs_manager.create_tables():
            print("TSRS tables created successfully.")
        else:
            print("Failed to create TSRS tables.")
    except Exception as e:
        print(f"Error initializing TSRS tables: {e}")

    # Initialize GRI Extension Tables
    try:
        print("Initializing GRI extension tables...")
        gri_upgrader = GRISchemaUpgrade()
        gri_upgrader.create_extension_tables()
        print("GRI extension tables created successfully.")
    except Exception as e:
        print(f"Error initializing GRI extension tables: {e}")

if __name__ == "__main__":
    init_tables()
