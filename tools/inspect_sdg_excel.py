import pandas as pd
import os

file_path = r'c:\SUSTAINAGESERVER\backend\data\SDG_16_169_232.xlsx'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    try:
        xls = pd.ExcelFile(file_path)
        print("Sheet names:", xls.sheet_names)
        
        for sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
            print(df.to_string())
            print("\nColumns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading Excel: {e}")
