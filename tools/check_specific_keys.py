
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

KEYS_TO_CHECK = [
    "category_environmental",
    "category_social",
    "category_governance",
    "category_compliance",
    "status_active",
    "status_pending",
    "completion",
    "action_enter_data",
    "action_enter_data_short",
    "action_view_details",
    "action_create_report",
    "performance_score",
    "data_fetch_error",
    "dashboard_load_error",
    "dashboard_title",
    "dark_mode",
    "light_mode",
    "share_button",
    "export_button",
    "average_score",
    "completed_reports",
    "next_deadline",
    "loading",
    "retry_button",
    "top_performance_metrics",
    "carbon_emissions",
    "survey_status",
    "system_alert_title",
    "pending_alerts_suffix",
    "dashboard_welcome",
    "login_title"
]

def check():
    tr_data = {}
    try:
        with open(os.path.join(LOCALES_DIR, 'tr.json'), 'r', encoding='utf-8') as f:
            tr_data = json.load(f)
    except:
        pass

    missing = []
    for key in KEYS_TO_CHECK:
        if key not in tr_data:
            missing.append(key)
            
    print(f"Missing in TR: {len(missing)}")
    for k in missing:
        print(f"  {k}")

if __name__ == "__main__":
    check()
