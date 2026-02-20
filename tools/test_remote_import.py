import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)
print(f"Added {BACKEND_DIR} to path")

try:
    import yonetim.license_manager
    print("Import yonetim.license_manager success")
except ImportError as e:
    print(f"Import yonetim.license_manager failed: {e}")
    print(f"Contents of {BACKEND_DIR}/yonetim:")
    try:
        print(os.listdir(os.path.join(BACKEND_DIR, 'yonetim')))
    except Exception as ex:
        print(f"Could not list dir: {ex}")

try:
    from modules.automated_reporting.auto_report import AutoReportManager
    print("Import AutoReportManager success")
except Exception as e:
    print(f"Import AutoReportManager failed: {e}")

try:
    from modules.analytics.trend_analyzer import TrendAnalyzer
    print("Import TrendAnalyzer success")
except Exception as e:
    print(f"Import TrendAnalyzer failed: {e}")
