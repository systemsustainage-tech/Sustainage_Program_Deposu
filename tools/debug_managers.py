import sys
import os
import sqlite3
from datetime import datetime

# Add project root and backend to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.modules.social.social_manager import SocialManager
from backend.modules.environmental.carbon_manager import CarbonManager

# Set DB Path
if os.name == 'nt':
    DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
else:
    DB_PATH = '/var/www/sustainage/backend/data/sustainability.db' # Remote path

def check_managers():
    if not os.path.exists(DB_PATH):
        # Fallback for remote if needed
        print(f"Warning: DB not found at {DB_PATH}")
        
    print(f"Checking DB: {DB_PATH}")
    company_id = 1
    
    # Check Social Manager
    print("\n--- Social Manager Stats ---")
    try:
        sm = SocialManager(DB_PATH)
        stats = sm.get_social_dashboard_stats(company_id)
        print(f"Stats: {stats}")
        
        # Simulate Dashboard Logic
        social_chart_data = [0, 0, 0, 0, 0]
        s_score = stats.get('satisfaction_score', 0)
        social_chart_data[0] = s_score if s_score else 0
        
        t_hours = stats.get('training_hours_total', 0)
        social_chart_data[1] = min(t_hours, 100) if t_hours else 0
        
        ohs_incidents = stats.get('ohs_incidents_total', 0)
        social_chart_data[2] = max(0, 100 - (ohs_incidents * 20)) if ohs_incidents is not None else 100
        
        hr_incidents = stats.get('human_rights_incidents', 0)
        social_chart_data[3] = max(0, 100 - (hr_incidents * 25)) if hr_incidents is not None else 100
        
        l_score = stats.get('labor_audit_avg_score', 0)
        social_chart_data[4] = l_score if l_score else 0
        
        print(f"Calculated Chart Data: {social_chart_data}")
        
    except Exception as e:
        print(f"Social Manager Error: {e}")

    # Check Carbon Manager
    print("\n--- Carbon Manager Stats ---")
    try:
        cm = CarbonManager(DB_PATH)
        current_year = 2025 # Using 2025 as seen in DB samples
        trend = cm.get_monthly_emission_stats(company_id, current_year)
        print(f"Emission Trend (Year {current_year}): {trend}")
        
        # Also check 2024
        trend_2024 = cm.get_monthly_emission_stats(company_id, 2024)
        print(f"Emission Trend (Year 2024): {trend_2024}")
        
    except Exception as e:
        print(f"Carbon Manager Error: {e}")

if __name__ == "__main__":
    check_managers()
