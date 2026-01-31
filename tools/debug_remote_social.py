import sys
import os

# Add the project root to sys.path
sys.path.append('/var/www/sustainage')

try:
    from backend.modules.social.social_manager import SocialManager
    print("SocialManager imported successfully.")
    
    manager = SocialManager('/var/www/sustainage/backend/data/sdg_desktop.sqlite')
    print("SocialManager initialized.")
    
    trends = manager.get_satisfaction_trends(1)
    print(f"Trends: {trends}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
