import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.modules.auto_tasks.auto_task_manager import AutoTaskManager
from backend.modules.visualization.visualization_manager import VisualizationManager

# Database path setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sustainage.db')
# Check if running on remote
if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

print(f"Using database: {DB_PATH}")

def add_dummy_data():
    company_id = 1 # Default company
    
    # 1. Auto Tasks
    try:
        atm = AutoTaskManager(DB_PATH, company_id=company_id)
        stats = atm.get_stats(company_id)
        if stats['total_tasks'] == 0:
            print("Adding dummy Auto Tasks...")
            atm.add_task(company_id, "Veri Yedekleme", "Günlük sistem ve veritabanı yedeği", "daily")
            atm.add_task(company_id, "Rapor Oluşturma", "Aylık sürdürülebilirlik raporu taslağı", "monthly")
            atm.add_task(company_id, "E-posta Bildirimleri", "Haftalık özet e-postaları gönderimi", "weekly")
            print("Auto Tasks added.")
        else:
            print(f"Auto Tasks already exist ({stats['total_tasks']}). Skipping.")
    except Exception as e:
        print(f"Error adding Auto Tasks: {e}")

    # 2. Visualization
    try:
        vm = VisualizationManager(DB_PATH, company_id=company_id)
        stats = vm.get_stats(company_id)
        if stats['total_charts'] == 0:
            print("Adding dummy Visualizations...")
            vm.add_visualization(company_id, "Karbon Emisyonu Trendi", "line", '{"x": "date", "y": "emission"}')
            vm.add_visualization(company_id, "Enerji Tüketim Dağılımı", "pie", '{"labels": ["Elektrik", "Doğalgaz"], "values": [70, 30]}')
            vm.add_visualization(company_id, "Atık Yönetimi Performansı", "bar", '{"x": "month", "y": "waste_kg"}')
            print("Visualizations added.")
        else:
            print(f"Visualizations already exist ({stats['total_charts']}). Skipping.")
    except Exception as e:
        print(f"Error adding Visualizations: {e}")

if __name__ == "__main__":
    add_dummy_data()
