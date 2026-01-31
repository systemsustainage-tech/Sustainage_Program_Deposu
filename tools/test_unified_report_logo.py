import os
import sys
import sqlite3
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.reporting.unified_report_docx import UnifiedReportDocxGenerator
from backend.modules.reporting.brand_identity_manager import BrandIdentityManager

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_logo_integration():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(base_dir, 'backend', 'data', 'sdg_desktop.sqlite')
    company_id = 1
    
    # 1. Find a test image
    test_logo = os.path.join(base_dir, 'static', 'images', 'SDGs.jpeg')
    if not os.path.exists(test_logo):
        # Create a dummy image if not exists (not ideal but fallback)
        print(f"Test image not found at {test_logo}, looking for any png/jpg...")
        # Try to find any image
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    test_logo = os.path.join(root, file)
                    break
            if test_logo != os.path.join(base_dir, 'static', 'images', 'SDGs.jpeg'):
                break
    
    if not os.path.exists(test_logo):
        print("No image found for testing logo integration.")
        return

    print(f"Using test logo: {test_logo}")

    # 2. Set brand identity
    bim = BrandIdentityManager(db_path, company_id)
    success = bim.save_brand_identity(
        company_id=company_id,
        logo_path=test_logo,
        colors={'primary': '#000000'},
        texts={'header': 'TEST REPORT HEADER'}
    )
    
    if success:
        print("Brand identity updated successfully.")
    else:
        print("Failed to update brand identity.")
        return

    # 3. Generate report
    generator = UnifiedReportDocxGenerator(base_dir)
    
    # Dummy data
    output_path = generator.generate(
        company_id=company_id,
        reporting_period="2024",
        report_name="Logo Integration Test",
        selected_modules=["SDG", "GRI"],
        module_reports=[],
        ai_comment="This is a test comment.",
        description="Test description",
        metrics={}
    )
    
    if output_path and os.path.exists(output_path):
        print(f"Report generated at: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        # Verify content? Hard to verify docx content without parsing, but size > 0 is good start.
        # We rely on the fact that code didn't crash.
    else:
        print("Report generation failed.")

if __name__ == "__main__":
    test_logo_integration()
