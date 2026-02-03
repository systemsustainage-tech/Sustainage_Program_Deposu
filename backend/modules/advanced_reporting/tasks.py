import os
import sys
import logging
from backend.celery_app import celery
from config.database import DB_PATH
from backend.modules.advanced_reporting.reporting_service import ReportingService
from backend.modules.advanced_reporting.report_engine import ReportEngine

# Ensure correct path for output
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'static', 'reports')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@celery.task(bind=True)
def generate_report_task(self, company_id, period, scope, report_id):
    """
    Celery task to generate report in background.
    """
    try:
        self.update_state(state='STARTED', meta={'status': 'Initializing services...'})
        
        # Initialize services
        # FORCE DB_PATH for remote environment if needed, similar to web_app.py
        current_db_path = DB_PATH
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            current_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
            
        service = ReportingService(current_db_path)
        engine = ReportEngine(OUTPUT_DIR)
        
        # Step 1: Collect Data
        self.update_state(state='PROGRESS', meta={'status': 'Collecting data from modules...'})
        data = service.collect_data(company_id, period, scope)
        
        if 'error' in data:
            raise Exception(data['error'])
            
        # Step 2: Generate Report
        self.update_state(state='PROGRESS', meta={'status': 'Generating PDF and JSON...'})
        result = engine.generate_report(data, report_id)
        
        return {
            'status': 'Completed',
            'result': result
        }
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise e
