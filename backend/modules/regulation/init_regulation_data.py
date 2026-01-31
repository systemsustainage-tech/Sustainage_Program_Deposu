import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import config for correct DB path
try:
    from config.database import DB_PATH
except ImportError:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    sys.path.insert(0, base_dir)
    from config.database import DB_PATH

try:
    from backend.modules.regulation.regulation_manager import RegulationManager
except ImportError:
    from modules.regulation.regulation_manager import RegulationManager

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print(f"Populating regulations in: {DB_PATH}")
    rm = RegulationManager(DB_PATH)
    rm.populate_initial_data()
    
    # Verify
    regs = rm.get_regulations()
    print(f"Total regulations: {len(regs)}")
    for r in regs:
        print(f"- {r['code']}: {r['compliance_deadline']}")
