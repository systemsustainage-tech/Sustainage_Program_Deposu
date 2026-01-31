import json
import os

file_path = 'c:\\SUSTAINAGESERVER\\locales\\tr.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Sort keys
    sorted_data = dict(sorted(data.items()))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully cleaned and sorted {len(sorted_data)} keys.")
except Exception as e:
    print(f"Error: {e}")
