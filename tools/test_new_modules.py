import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.config.database import DB_PATH
from backend.modules.auto_tasks.auto_task_manager import AutoTaskManager
from backend.modules.visualization.visualization_manager import VisualizationManager

def test_modules():
    print("Testing AutoTaskManager...")
    try:
        atm = AutoTaskManager(DB_PATH, company_id=1)
        stats = atm.get_stats(1)
        print(f"AutoTaskManager stats: {stats}")
        records = atm.get_records(1)
        print(f"AutoTaskManager records: {len(records)}")
    except Exception as e:
        print(f"AutoTaskManager FAILED: {e}")

    print("\nTesting VisualizationManager...")
    try:
        vm = VisualizationManager(DB_PATH, company_id=1)
        stats = vm.get_stats(1)
        print(f"VisualizationManager stats: {stats}")
        records = vm.get_records(1)
        print(f"VisualizationManager records: {len(records)}")
    except Exception as e:
        print(f"VisualizationManager FAILED: {e}")

if __name__ == "__main__":
    test_modules()
