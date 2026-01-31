
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os

# Add the current directory and backend directory to sys.path to resolve imports
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Define DB Path same as web_app.py
BACKEND_DIR = os.path.join(os.getcwd(), 'backend')
DB_PATH = os.path.join(BACKEND_DIR, 'data', 'sdg_desktop.sqlite')

from backend.modules.environmental.carbon_manager import CarbonManager
from backend.modules.environmental.energy_manager import EnergyManager
from backend.modules.environmental.waste_manager import WasteManager
from backend.modules.environmental.water_manager import WaterManager
from backend.modules.environmental.biodiversity_manager import BiodiversityManager
from backend.modules.social.social_manager import SocialManager
from backend.modules.governance.corporate_governance import CorporateGovernanceManager
from backend.modules.supply_chain.supply_chain_manager import SupplyChainManager
from backend.modules.economic.economic_value_manager import EconomicValueManager

def verify_managers():
    company_id = 1
    managers = {
        'carbon': CarbonManager(DB_PATH),
        'energy': EnergyManager(DB_PATH),
        'waste': WasteManager(DB_PATH),
        'water': WaterManager(DB_PATH),
        'biodiversity': BiodiversityManager(DB_PATH),
        'social': SocialManager(DB_PATH),
        'governance': CorporateGovernanceManager(DB_PATH),
        'supply_chain': SupplyChainManager(DB_PATH),
        'economic': EconomicValueManager(DB_PATH)
    }

    for name, manager in managers.items():
        print(f"Checking {name}...")
        try:
            if hasattr(manager, 'get_dashboard_stats'):
                stats = manager.get_dashboard_stats(company_id)
                print(f"  - get_dashboard_stats: OK ({list(stats.keys())})")
            elif hasattr(manager, 'get_stats'):
                stats = manager.get_stats(company_id)
                print(f"  - get_stats: OK ({list(stats.keys())})")
            else:
                print(f"  - WARNING: No stats method found!")
            
            if hasattr(manager, 'get_recent_records'):
                data = manager.get_recent_records(company_id)
                print(f"  - get_recent_records: OK (Count: {len(data)})")
            elif hasattr(manager, 'get_recent_data'):
                data = manager.get_recent_data(company_id)
                print(f"  - get_recent_data: OK (Count: {len(data)})")
            else:
                print(f"  - WARNING: No recent data method found!")
                
        except Exception as e:
            print(f"  - ERROR: {e}")

if __name__ == "__main__":
    verify_managers()
