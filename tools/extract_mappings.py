
import pandas as pd
import os

def extract_mappings():
    file_path = 'SDG_232.xlsx'
    if not os.path.exists(file_path):
        print("Excel file not found.")
        return

    try:
        xl = pd.ExcelFile(file_path)
        print("Sheet names:", xl.sheet_names)
        
        if 'MASTER_232' in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name='MASTER_232')
            print("Columns in MASTER_232:", df.columns.tolist())
            esrs_cols = [c for c in df.columns if 'ESRS' in c]
            print("ESRS Columns:", esrs_cols)
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    extract_mappings()
