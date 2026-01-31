import json
import os
import sys

# Mocking the path relative to where web_app.py is usually run
base_path = os.getcwd()
json_path = os.path.join(base_path, 'backend', 'data', 'stakeholder_questions.json')

print(f"Checking JSON path: {json_path}")

try:
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Successfully loaded JSON.")
            print(f"Available groups: {list(data.keys())}")
            
            # Test 'customers' group logic
            group = 'customers'
            if group in data:
                questions = data[group].get('questions', [])
                print(f"\nSimulating selection of '{group}':")
                print(f"Found {len(questions)} questions.")
                for q in questions[:3]: # Show first 3
                    print(f"- [{q.get('category')}] {q.get('text')} (Type: {q.get('type')})")
            else:
                print(f"Group {group} not found!")
    else:
        print("JSON file not found.")
except Exception as e:
    print(f"Error: {e}")
