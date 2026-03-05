import logging
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from backend.core.base_manager import BaseTenantManager

class DashboardStatsManager(BaseTenantManager):
    def __init__(self, db_path):
        super().__init__(db_path)

    def get_module_stats(self, company_id):
        """
        Calculates completion percentage for each module.
        Returns a dictionary {module_key: percentage_int}.
        """
        stats = {}
        # Mapping: module_key -> (table_name, target_count)
        # target_count is a heuristic for 100% completion.
        # If target_count is None, just presence (>0) means 100%.
        
        module_config = {
            'carbon': ('carbon_emissions', 4),       # Quarterly data?
            'energy': ('energy_consumption', 4),
            'waste': ('waste_generation', 4),
            'water': ('water_consumption', 4),
            'biodiversity': ('biodiversity_sites', 1),
            
            'social': ('social_employees', 1),       # Basic HR data
            'governance': ('board_members', 3),      # At least 3 board members
            'supply_chain': ('suppliers', 5),        # At least 5 suppliers
            'economic': ('economic_value_distribution', 1),
            
            'esg': ('esg_scores', 1),
            'cbam': ('cbam_reports', 1),
            'csrd': ('csrd_compliance_checklist', 10), # 10 checklist items?
            'taxonomy': ('eu_taxonomy_alignment', 1),
            'gri': ('gri_responses', 10),            # 10 indicators reported
            'sdg': ('sdg_progress', 1),              # Goals selected/progress
            'esrs': ('esrs_assessments', 5),
            
            'prioritization': ('materiality_topics', 5), # Top 5 topics
            'issb': ('issb_reporting_status', 1),    # Renamed from ifrs
            'tcfd': ('tcfd_disclosures', 4),         # 4 pillars
            'tnfd': ('tnfd_disclosures', 4),
            'cdp': ('cdp_scoring', 1),
            'product_technology': ('innovation_metrics', 1),
            'regulation': ('regulation_compliance', 1),
            'unified_report': ('unified_reports', 1), # Assuming table exists
            'benchmark': ('sector_averages', 1)       # System data
        }
        
        try:
            # Check which tables exist to avoid errors
            # Using direct DB query for sqlite_master (global)
            rows = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row['name'] for row in rows}
            
            for key, (table, target) in module_config.items():
                if table not in existing_tables:
                    stats[key] = 0
                    continue
                    
                try:
                    # BaseTenantManager.execute_query will automatically inject company_id filter
                    # We just provide the base query
                    rows = self.execute_query(f"SELECT COUNT(*) FROM {table}", company_id=company_id)
                    count = rows[0][0] if rows else 0
                    
                    if target is None:
                        percentage = 100 if count > 0 else 0
                    else:
                        percentage = min(int((count / target) * 100), 100)
                    
                    stats[key] = percentage
                    
                except Exception as e:
                    logging.error(f"Error calculating stats for {key} ({table}): {e}")
                    stats[key] = 0
            
        except Exception as e:
            logging.error(f"DashboardStatsManager error: {e}")
            
        return stats
