
import json
import os

keys_to_check = [
    "btn_back", "btn_add_data", "gov_title", "governance_title", 
    "gov_board_members", "gov_ethics_compliance", "gov_manager_active",
    "gov_board_members_stat", "gov_training_hours", "recent_activities",
    "col_type", "col_detail", "col_date", "gov_board", "gov_committee",
    "gov_ethics", "no_data_yet", "manager_failed",
    "btn_new_report"
]

def check_keys():
    try:
        with open('locales/tr.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        missing = []
        for k in keys_to_check:
            if k not in data:
                missing.append(k)
        
        if missing:
            print(f"MISSING KEYS: {missing}")
        else:
            print("ALL KEYS FOUND")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_keys()
