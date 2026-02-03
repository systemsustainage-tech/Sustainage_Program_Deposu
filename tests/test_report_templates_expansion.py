
import logging
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.advanced_reporting.report_templates import AdvancedReportTemplates

def test_template_expansion():
    """Test the expansion of report templates"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Testing Report Template Expansion...")
    
    # Initialize
    db_path = 'tests/test_sdg_desktop.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    templates = AdvancedReportTemplates(db_path=db_path)
    
    # 1. Verify Templates Loaded
    available = templates.get_available_templates()
    logging.info(f"Loaded {len(available)} templates.")
    
    # Check for expected templates
    expected_ids = [
        'carbon_template_en', 'carbon_template_de',
        'cbam_template_en', 'cbam_template_de',
        'tcfd_template_en', 'tcfd_template_de',
        'sdg_template_tr_html', 'carbon_template_en_html'
    ]
    
    loaded_ids = [t['id'] for t in available]
    for eid in expected_ids:
        if eid in loaded_ids:
            logging.info(f"[OK] Template found: {eid}")
        else:
            logging.error(f"[FAIL] Template missing: {eid}")

    # 2. Test Data
    test_data = {
        'company_name': 'Test International Corp',
        'sdg_data': {'SDG 7': 85.0, 'SDG 13': 60.0},
        'emissions': {
            'total': 1234.56, 
            'scope_breakdown': {'scope1': 500, 'scope2': 734.56},
            'total_embedded': 450.0
        },
        'carbon_price': 85.50,
        'declarant_name': 'John Doe',
        'goods': [
            {'cn_code': '7208', 'quantity': 100, 'embedded': 250, 'indirect': 50}
        ],
        'tcfd_governance': 'Board oversight of climate risks.',
        'tcfd_strategy': 'Transition to renewable energy.',
        'tcfd_risk': 'Physical and transition risks identified.',
        'tcfd_metrics': 'Scope 1, 2, 3 emissions tracked.'
    }

    # 3. Generate Reports
    reports_to_test = [
        ('carbon_template_en', 'Carbon Footprint Report (EN)'),
        ('cbam_template_de', 'CBAM Report (DE)'),
        ('tcfd_template_tr', 'TCFD Report (TR)'),
        ('sdg_template_en_html', 'SDG HTML Preview (EN)'),
        ('cbam_template_en_html', 'CBAM HTML Preview (EN)')
    ]
    
    for tid, desc in reports_to_test:
        logging.info(f"Generating {desc}...")
        path = templates.generate_report(tid, 999, '2025-Q1', test_data)
        if path and os.path.exists(path):
            logging.info(f"[OK] Generated: {path}")
            # Verify HTML content
            if tid.endswith('_html'):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '<html' in content and 'Test International Corp' in content:
                        logging.info(f"[OK] HTML content verified for {tid}")
                    else:
                        logging.error(f"[FAIL] HTML content invalid for {tid}")
        else:
            logging.error(f"[FAIL] Generation failed for {tid}")

if __name__ == "__main__":
    test_template_expansion()
