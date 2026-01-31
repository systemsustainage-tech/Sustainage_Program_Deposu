
import sys
import os
import logging

# Setup environment
sys.path.insert(0, r'c:\SUSTAINAGESERVER\backend')
sys.path.insert(0, r'c:\SUSTAINAGESERVER')

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

logging.basicConfig(level=logging.INFO)

print("Checking Manager Imports...")

managers_to_check = [
    ('sdg', 'modules.sdg.sdg_manager', 'SDGManager'),
    ('gri', 'modules.gri.gri_manager', 'GRIManager'),
    ('social', 'modules.social.social_manager', 'SocialManager'),
    ('governance', 'modules.governance.corporate_governance', 'CorporateGovernanceManager'),
    ('carbon', 'modules.environmental.carbon_manager', 'CarbonManager'),
    ('energy', 'modules.environmental.energy_manager', 'EnergyManager'),
    ('esg', 'modules.esg.esg_manager', 'ESGManager'),
    ('cbam', 'modules.cbam.cbam_manager', 'CBAMManager'),
    ('csrd', 'modules.csrd.csrd_compliance_manager', 'CSRDComplianceManager'),
    ('taxonomy', 'modules.eu_taxonomy.taxonomy_manager', 'EUTaxonomyManager'),
    ('waste', 'modules.environmental.waste_manager', 'WasteManager'),
    ('water', 'modules.environmental.water_manager', 'WaterManager'),
    ('biodiversity', 'modules.environmental.biodiversity_manager', 'BiodiversityManager'),
    ('economic', 'modules.economic.economic_value_manager', 'EconomicValueManager'),
    ('supply_chain', 'modules.economic.supply_chain_manager', 'SupplyChainManager'),
    ('cdp', 'modules.cdp.cdp_manager', 'CDPManager'),
    ('issb', 'modules.issb.issb_manager', 'ISSBManager'),
    ('iirc', 'modules.iirc.iirc_manager', 'IIRCManager'),
    ('esrs', 'modules.esrs.esrs_manager', 'ESRSManager'),
    ('tcfd', 'modules.tcfd.tcfd_manager', 'TCFDManager'),
    ('tnfd', 'modules.tnfd.tnfd_manager', 'TNFDManager'),
]

for name, module_path, class_name in managers_to_check:
    try:
        mod = __import__(module_path, fromlist=[class_name])
        cls = getattr(mod, class_name)
        # Try instantiation
        instance = cls(DB_PATH)
        print(f"[OK] {name} - {class_name}")
    except Exception as e:
        print(f"[FAIL] {name} - {class_name}: {e}")

