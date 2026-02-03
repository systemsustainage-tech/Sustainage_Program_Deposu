import logging
import json
from typing import Dict, Any, Optional

# Import Managers
# Note: These imports assume that 'backend' or the parent of 'modules' is in sys.path
try:
    from backend.modules.environmental.carbon_manager import CarbonManager
    from backend.modules.environmental.water_manager import WaterManager
    from backend.modules.environmental.waste_manager import WasteManager
    from backend.modules.environmental.biodiversity_manager import BiodiversityManager
    from backend.modules.social.social_manager import SocialManager
    from backend.modules.governance.corporate_governance import CorporateGovernanceManager
    from backend.modules.supply_chain.supply_chain_manager import SupplyChainManager
except ImportError:
    try:
        from modules.environmental.carbon_manager import CarbonManager
        from modules.environmental.water_manager import WaterManager
        from modules.environmental.waste_manager import WasteManager
        from modules.environmental.biodiversity_manager import BiodiversityManager
        from modules.social.social_manager import SocialManager
        from modules.governance.corporate_governance import CorporateGovernanceManager
        from modules.supply_chain.supply_chain_manager import SupplyChainManager
    except ImportError as e:
        logging.error(f"Error importing managers in ReportingService: {e}")

class ReportingService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Initialize managers
        self.carbon_manager = CarbonManager(db_path)
        self.water_manager = WaterManager(db_path)
        self.waste_manager = WasteManager(db_path)
        self.biodiversity_manager = BiodiversityManager(db_path)
        self.social_manager = SocialManager(db_path)
        self.governance_manager = CorporateGovernanceManager(db_path)
        self.supply_chain_manager = SupplyChainManager(db_path)

    def collect_data(self, company_id: int, period: str, scope: str = 'full') -> Dict[str, Any]:
        """
        Collects data from various modules for the given company and period.
        
        Args:
            company_id: The ID of the company.
            period: The reporting period (e.g., '2024', '2024-Q1').
            scope: The scope of the report ('full', 'environmental', 'social', 'governance').
            
        Returns:
            A dictionary containing the collected data.
        """
        data = {
            'company_id': company_id,
            'period': period,
            'scope': scope,
            'generated_at': None, # To be filled by the caller or engine
            'modules': {}
        }

        try:
            # Environmental
            if scope in ['full', 'environmental']:
                data['modules']['environmental'] = {
                    'carbon': self._get_carbon_data(company_id, period),
                    'water': self._get_water_data(company_id, period),
                    'waste': self._get_waste_data(company_id, period),
                    'biodiversity': self._get_biodiversity_data(company_id, period)
                }

            # Social
            if scope in ['full', 'social']:
                data['modules']['social'] = self._get_social_data(company_id, period)

            # Governance
            if scope in ['full', 'governance']:
                data['modules']['governance'] = self._get_governance_data(company_id, period)
                
            # Supply Chain (Usually part of full or specific scope, putting in full for now)
            if scope == 'full':
                data['modules']['supply_chain'] = self._get_supply_chain_data(company_id, period)

        except Exception as e:
            logging.error(f"Error collecting report data: {e}")
            data['error'] = str(e)

        return data

    def _get_carbon_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            # Assuming managers have methods to get stats or data by year/period
            # Adapting to what is likely available based on typical manager patterns
            # If get_stats takes year as int:
            year = int(period.split('-')[0]) if '-' in period else int(period)
            return self.carbon_manager.get_dashboard_stats(company_id, year)
        except Exception as e:
            logging.warning(f"Failed to get carbon data: {e}")
            return {}

    def _get_water_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            # WaterManager might not have get_stats with year, checking previous exploration
            # It had get_efficiency_projects(company_id). 
            # I will return a basic summary if specific period method is missing.
            return {
                'efficiency_projects': self.water_manager.get_efficiency_projects(company_id)
            }
        except Exception as e:
            logging.warning(f"Failed to get water data: {e}")
            return {}

    def _get_waste_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            # Assuming get_summary or similar exists
            return self.waste_manager.get_summary(company_id) if hasattr(self.waste_manager, 'get_summary') else {}
        except Exception as e:
            logging.warning(f"Failed to get waste data: {e}")
            return {}

    def _get_biodiversity_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            year = int(period.split('-')[0]) if '-' in period else int(period)
            return self.biodiversity_manager.get_dashboard_stats(company_id, year) if hasattr(self.biodiversity_manager, 'get_dashboard_stats') else {}
        except Exception as e:
            logging.warning(f"Failed to get biodiversity data: {e}")
            return {}

    def _get_social_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            return self.social_manager.get_dashboard_stats(company_id) if hasattr(self.social_manager, 'get_dashboard_stats') else {}
        except Exception as e:
            logging.warning(f"Failed to get social data: {e}")
            return {}

    def _get_governance_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            return self.governance_manager.get_dashboard_stats(company_id) if hasattr(self.governance_manager, 'get_dashboard_stats') else {}
        except Exception as e:
            logging.warning(f"Failed to get governance data: {e}")
            return {}

    def _get_supply_chain_data(self, company_id: int, period: str) -> Dict[str, Any]:
        try:
            return self.supply_chain_manager.get_dashboard_stats(company_id) if hasattr(self.supply_chain_manager, 'get_dashboard_stats') else {}
        except Exception as e:
            logging.warning(f"Failed to get supply chain data: {e}")
            return {}
