
import json

try:
    with open('backend/locales/tr.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    keys_to_check = [
        "Select Template", "select_template", 
        "No Data Msg", "no_data_msg",
        "Stakeholder Name", "stakeholder_name",
        "Training Name", "training_name",
        "Add Training Program", "add_training_program",
        "Add Training Record", "add_training_record",
        "Add First Topic", "add_first_topic"
    ]
    
    print("Checking keys in backend/locales/tr.json:")
    for k in keys_to_check:
        if k in data:
            print(f"Found '{k}': '{data[k]}'")
        else:
            print(f"Missing '{k}'")
            
except Exception as e:
    print(f"Error: {e}")
