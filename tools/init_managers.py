
import sys
import os
import logging

# Add backend to path FIRST to avoid config shadowing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.modules.sdg.sdg_manager import SDGManager
from backend.modules.iirc.iirc_manager import IIRCManager
from backend.modules.csrd.csrd_compliance_manager import CSRDComplianceManager

logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing managers to ensure tables exist...")
    
    try:
        print("Initializing SDGManager...")
        sdg = SDGManager()
        print("SDG tables initialized.")
    except Exception as e:
        print(f"Error initializing SDGManager: {e}")

    try:
        print("Initializing IIRCManager...")
        iirc = IIRCManager()
        print("IIRC tables initialized.")
    except Exception as e:
        print(f"Error initializing IIRCManager: {e}")

    try:
        print("Initializing CSRDComplianceManager...")
        csrd = CSRDComplianceManager()
        print("CSRD tables initialized.")
    except Exception as e:
        print(f"Error initializing CSRDComplianceManager: {e}")

if __name__ == "__main__":
    main()
