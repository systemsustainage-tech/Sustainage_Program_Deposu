import sqlite3
import logging

class DashboardStatsManager:
    def __init__(self, db_path):
        self.db_path = db_path

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
            'ifrs': ('issb_reporting_status', 1),
            'tcfd': ('tcfd_disclosures', 4),         # 4 pillars
            'tnfd': ('tnfd_disclosures', 4),
            'cdp': ('cdp_scoring', 1)
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check which tables exist to avoid errors
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            for key, (table, target) in module_config.items():
                if table not in existing_tables:
                    stats[key] = 0
                    continue
                    
                try:
                    # Try to filter by company_id if possible
                    # We first check if company_id column exists by selecting 1 row
                    # Or simpler: try/except the query with company_id
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE company_id=?", (company_id,))
                        count = cursor.fetchone()[0]
                    except sqlite3.OperationalError:
                        # Column company_id might not exist
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                    
                    if target is None:
                        percentage = 100 if count > 0 else 0
                    else:
                        percentage = min(int((count / target) * 100), 100)
                    
                    stats[key] = percentage
                    
                except Exception as e:
                    logging.error(f"Error calculating stats for {key} ({table}): {e}")
                    stats[key] = 0
            
            conn.close()
            
        except Exception as e:
            logging.error(f"DashboardStatsManager error: {e}")
            
        return stats
