import sqlite3
import datetime
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def add_sample_data():
    print(f"Connecting to database at {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        company_id = 1
        
        # Clear existing data for cleaner test
        print("Clearing existing social data for company 1...")
        try:
            cursor.execute("DELETE FROM employee_satisfaction WHERE company_id = ?", (company_id,))
            cursor.execute("DELETE FROM community_investment WHERE company_id = ?", (company_id,))
        except sqlite3.OperationalError as e:
            print(f"Warning during delete (tables might not exist): {e}")
        
        # Employee Satisfaction Data (3 years)
        satisfaction_data = [
            (company_id, 2023, '2023-12-01', 75.5, 12.0, 85.0, 'Good year'),
            (company_id, 2024, '2024-12-01', 78.0, 10.5, 88.0, 'Improved benefits'),
            (company_id, 2025, '2025-12-01', 82.5, 8.0, 92.0, 'Remote work options')
        ]
        
        print("Inserting employee satisfaction data...")
        cursor.executemany("""
            INSERT INTO employee_satisfaction 
            (company_id, year, survey_date, satisfaction_score, turnover_rate, participation_rate, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, satisfaction_data)
        
        print(f"Added {len(satisfaction_data)} employee satisfaction records.")
        
        # Community Investment Data
        investment_data = [
            (company_id, 'Local School Support', 50000.0, 200, 'Provided computers', '2023-05-15'),
            (company_id, 'Tree Planting', 15000.0, 1000, 'Planted 500 trees', '2024-04-22'),
            (company_id, 'Youth Coding Camp', 35000.0, 50, 'Summer coding bootcamp', '2025-07-10')
        ]
        
        print("Inserting community investment data...")
        cursor.executemany("""
            INSERT INTO community_investment 
            (company_id, project_name, investment_amount, beneficiaries_count, impact_description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, investment_data)
        
        print(f"Added {len(investment_data)} community investment records.")
        
        conn.commit()
        conn.close()
        print("Sample data added successfully.")
        
    except Exception as e:
        print(f"Error adding data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_sample_data()
