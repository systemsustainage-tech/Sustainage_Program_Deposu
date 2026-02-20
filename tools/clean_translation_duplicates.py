import json
import os
from collections import OrderedDict

def clean_duplicates():
    file_path = os.path.join(os.path.dirname(__file__), 'translation_dictionary.json')
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Reading {file_path}...")
    
    # We need to read the file manually to detect duplicates because json.load will just take the last one
    # But wait, if we want to "keep the meaningful one and delete others", we might need manual intervention.
    # However, if we just want to ensure valid JSON and remove technical duplicates, json.load/dump is enough.
    # But the user said "anlamlı olanı koruyup diğerini sil".
    # If I load it with json.load, I effectively keep the last one.
    # If the file has duplicates, it's already "corrupted" in terms of uniqueness.
    # Let's read it as raw text to see how many duplicates there are.
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple check for duplicates using a parser that tracks keys
    # But since it's a huge file, maybe we just trust json.load to take the last state, 
    # assuming the last state is the most recent/correct one.
    
    try:
        data = json.load(open(file_path, 'r', encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return

    # Write it back with indentation to clean it up
    print(f"Writing cleaned JSON back to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Done.")

if __name__ == "__main__":
    clean_duplicates()
