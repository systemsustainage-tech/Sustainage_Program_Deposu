
import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

from mapping.sdg_gri_mapping import SDGGRIMapping

logging.basicConfig(level=logging.INFO)

def check_mapping():
    print("Initializing SDGGRIMapping...")
    try:
        mapper = SDGGRIMapping()
        print("Mapper initialized.")
    except Exception as e:
        print(f"Failed to initialize mapper: {e}")
        return

    print("Testing get_questions_for_goals([6])...")
    try:
        data = mapper.get_questions_for_goals([6])
        print(f"Result count: {len(data)}")
        if data:
            print("First item sample:")
            print(data[0])
        else:
            print("No data returned. Check if Excel file exists and has data for Goal 6.")
            
            # Check Excel file existence
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
            excel_path = os.path.join(base_dir, 'SDG_232.xlsx')
            print(f"Checking for Excel at: {excel_path}")
            if os.path.exists(excel_path):
                print("Excel file exists.")
            else:
                print("Excel file MISSING!")

    except Exception as e:
        print(f"Error during get_questions_for_goals: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mapping()
