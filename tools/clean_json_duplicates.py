import json
import sys
import os

def clean_duplicates(file_path):
    print(f"Cleaning duplicates in {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f) # This automatically handles duplicates by keeping the last one
        
        # Sort keys for better diffs
        sorted_data = dict(sorted(data.items()))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)
            
        print("Done. Duplicates removed (last one kept) and keys sorted.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        clean_duplicates(sys.argv[1])
    else:
        print("Usage: python clean_json_duplicates.py <file_path>")
